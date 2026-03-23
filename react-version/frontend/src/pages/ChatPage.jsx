import React, { useState, useRef, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { FaPaperPlane, FaImage, FaTrash, FaRobot, FaHome, FaStop, FaTachometerAlt, FaPlay, FaPause } from 'react-icons/fa';
import './ChatPage.css';

const API_BASE = 'http://localhost:8000';

function ChatPage() {
  const navigate = useNavigate();
  const [messages, setMessages] = useState([]);
  const [inputText, setInputText] = useState('');
  const [selectedImage, setSelectedImage] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [voiceEnabled, setVoiceEnabled] = useState(true);
  const [voiceSpeed, setVoiceSpeed] = useState(1.4);
  const [metrics, setMetrics] = useState({
    lastResponseTime: 0,
    avgResponseTime: 0,
    totalTokens: 0,
    messagesCount: 0
  });

  const messagesEndRef = useRef(null);
  const fileInputRef = useRef(null);
  const currentAudioRef = useRef(null);
  const abortControllerRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(scrollToBottom, [messages]);

  const stopCurrentAudio = () => {
    if (currentAudioRef.current) {
      currentAudioRef.current.pause();
      currentAudioRef.current.currentTime = 0;
      currentAudioRef.current = null;
    }
  };

  const abortOngoingRequest = () => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      abortControllerRef.current = null;
    }
  };

  // Resize image to max 512px before upload to speed up LLaVA
  const resizeImage = (file, maxPx = 512) => new Promise((resolve) => {
    const img = document.createElement('img');
    const url = URL.createObjectURL(file);
    img.onload = () => {
      const scale = Math.min(maxPx / img.width, maxPx / img.height, 1);
      const canvas = document.createElement('canvas');
      canvas.width = Math.round(img.width * scale);
      canvas.height = Math.round(img.height * scale);
      canvas.getContext('2d').drawImage(img, 0, 0, canvas.width, canvas.height);
      URL.revokeObjectURL(url);
      canvas.toBlob(resolve, 'image/jpeg', 0.85);
    };
    img.src = url;
  });

  // Consume an SSE stream and call onToken for each token; returns full content
  const readSSEStream = async (response, onToken) => {
    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = '';
    let fullContent = '';

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split('\n');
      buffer = lines.pop();
      for (const line of lines) {
        if (!line.startsWith('data: ')) continue;
        const data = line.slice(6).trim();
        if (data === '[DONE]') break;
        try {
          const parsed = JSON.parse(data);
          if (parsed.token) {
            fullContent += parsed.token;
            onToken(fullContent);
          }
        } catch (_) {}
      }
    }
    return fullContent;
  };

  const handleSendMessage = async () => {
    if (!inputText.trim() && !selectedImage) return;
    if (isLoading) return;

    stopCurrentAudio();
    abortOngoingRequest();

    abortControllerRef.current = new AbortController();

    const userMessage = {
      role: 'user',
      content: inputText,
      image: selectedImage ? URL.createObjectURL(selectedImage) : null
    };

    const messageText = inputText;
    const messageImage = selectedImage;

    setInputText('');
    setSelectedImage(null);
    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);

    const startTime = Date.now();

    try {
      let fullContent = '';

      // Add empty assistant message — works for both text and image
      setMessages(prev => [...prev, { role: 'assistant', content: '' }]);

      const onToken = (content) => {
        setMessages(prev => {
          const updated = [...prev];
          updated[updated.length - 1] = { role: 'assistant', content };
          return updated;
        });
      };

      if (messageImage) {
        // Resize image before upload, then stream
        const resized = await resizeImage(messageImage);
        const formData = new FormData();
        formData.append('message', messageText || 'Describe this property');
        formData.append('image', resized, 'image.jpg');

        const response = await fetch(`${API_BASE}/api/chat-with-image`, {
          method: 'POST',
          body: formData,
          signal: abortControllerRef.current.signal
        });
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        fullContent = await readSSEStream(response, onToken);
      } else {
        // Text chat — SSE streaming
        const formData = new FormData();
        formData.append('message', messageText);

        const response = await fetch(`${API_BASE}/api/chat`, {
          method: 'POST',
          body: formData,
          signal: abortControllerRef.current.signal
        });
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        fullContent = await readSSEStream(response, onToken);
      }

      const endTime = Date.now();
      const responseTime = (endTime - startTime) / 1000;
      setMessages(prev => {
        const updated = [...prev];
        updated[updated.length - 1] = { role: 'assistant', content: fullContent, responseTime };
        return updated;
      });
      const tokenEstimate = fullContent.split(' ').length * 1.3;
      setMetrics(prev => ({
        lastResponseTime: responseTime,
        avgResponseTime: ((prev.avgResponseTime * prev.messagesCount) + responseTime) / (prev.messagesCount + 1),
        totalTokens: prev.totalTokens + Math.round(tokenEstimate),
        messagesCount: prev.messagesCount + 1
      }));

      // Unblock UI before TTS
      setIsLoading(false);

      // Text to speech (non-blocking)
      if (voiceEnabled && fullContent) {
        try {
          const ttsFormData = new FormData();
          ttsFormData.append('text', fullContent);
          const ttsResponse = await axios.post(`${API_BASE}/api/text-to-speech`, ttsFormData);

          const audio = new Audio(`${API_BASE}${ttsResponse.data.audio_url}`);
          audio.playbackRate = voiceSpeed;
          currentAudioRef.current = audio;
          audio.onended = () => { currentAudioRef.current = null; };
          audio.play().catch(err => console.error('Audio play error:', err));
        } catch (ttsError) {
          console.error('TTS Error:', ttsError);
        }
      }
    } catch (error) {
      if (error.name === 'AbortError' || error.name === 'CanceledError' || error.code === 'ERR_CANCELED') {
        console.log('Request canceled');
        return;
      }

      console.error('Error:', error);
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: 'Sorry, there was an error processing your request.'
      }]);
    } finally {
      setIsLoading(false);
      abortControllerRef.current = null;
    }
  };

  const handleImageUpload = (e) => {
    const file = e.target.files[0];
    if (file && file.type.startsWith('image/')) {
      setSelectedImage(file);
    }
  };

  const clearChat = () => {
    stopCurrentAudio();
    abortOngoingRequest();
    setMessages([]);
    setSelectedImage(null);
    setMetrics({
      lastResponseTime: 0,
      avgResponseTime: 0,
      totalTokens: 0,
      messagesCount: 0
    });
  };

  const toggleAudioPlayback = () => {
    if (currentAudioRef.current) {
      if (currentAudioRef.current.paused) {
        currentAudioRef.current.play();
      } else {
        currentAudioRef.current.pause();
      }
    }
  };

  return (
    <div className="chat-page">
      <div className="sidebar">
        <div className="sidebar-header">
          <h2>🏠 Real Estate AI</h2>
          <button className="home-btn" onClick={() => navigate('/')}>
            <FaHome /> Home
          </button>
        </div>

        <div className="metrics-panel">
          <h3>📊 Performance Metrics</h3>
          <div className="metric-item">
            <span className="metric-label">Last Response</span>
            <span className="metric-value">{metrics.lastResponseTime.toFixed(2)}s</span>
          </div>
          <div className="metric-item">
            <span className="metric-label">Avg Response</span>
            <span className="metric-value">{metrics.avgResponseTime.toFixed(2)}s</span>
          </div>
          <div className="metric-item">
            <span className="metric-label">Total Tokens</span>
            <span className="metric-value">{metrics.totalTokens}</span>
          </div>
          <div className="metric-item">
            <span className="metric-label">Messages</span>
            <span className="metric-value">{metrics.messagesCount}</span>
          </div>
        </div>

        <div className="model-info">
          <h3>🤖 Active Models</h3>
          <div className="model-card">
            <div className="model-name">Llama 3.1 8B</div>
            <div className="model-type">Text Generation</div>
          </div>
          <div className="model-card">
            <div className="model-name">LLaVA 7B</div>
            <div className="model-type">Vision + Text</div>
          </div>
        </div>

        <div className="sidebar-options">
          <button className="option-btn" onClick={() => fileInputRef.current.click()}>
            <FaImage /> Upload Image
          </button>
          <input
            ref={fileInputRef}
            type="file"
            accept="image/*"
            onChange={handleImageUpload}
            style={{ display: 'none' }}
          />

          <div className="voice-controls">
            <h4>🔊 Voice Controls</h4>

            <div className="toggle-option">
              <label>
                <input
                  type="checkbox"
                  checked={voiceEnabled}
                  onChange={(e) => setVoiceEnabled(e.target.checked)}
                />
                Enable Voice
              </label>
            </div>

            <div className="speed-control">
              <label>Speed: {voiceSpeed}x</label>
              <input
                type="range"
                min="0.5"
                max="2"
                step="0.1"
                value={voiceSpeed}
                onChange={(e) => {
                  setVoiceSpeed(parseFloat(e.target.value));
                  if (currentAudioRef.current) {
                    currentAudioRef.current.playbackRate = parseFloat(e.target.value);
                  }
                }}
              />
            </div>

            {currentAudioRef.current && (
              <div className="audio-controls">
                <button className="control-btn" onClick={toggleAudioPlayback}>
                  {currentAudioRef.current.paused ? <FaPlay /> : <FaPause />}
                </button>
                <button className="control-btn" onClick={stopCurrentAudio}>
                  <FaStop />
                </button>
              </div>
            )}
          </div>

          <button className="option-btn danger" onClick={clearChat}>
            <FaTrash /> Clear Chat
          </button>
        </div>

        {selectedImage && (
          <div className="selected-image-preview">
            <p>Selected Image:</p>
            <img src={URL.createObjectURL(selectedImage)} alt="Selected" />
            <button onClick={() => setSelectedImage(null)}>Remove</button>
          </div>
        )}
      </div>

      <div className="main-chat">
        <div className="chat-header">
          <div>
            <h1>Abu Dhabi Real Estate Assistant</h1>
            <p>Ask about properties, prices, locations, and more!</p>
          </div>
          <div className="header-status">
            <span className="status-dot"></span>
            <span>Models Active</span>
          </div>
        </div>

        <div className="messages-container">
          {messages.length === 0 && (
            <div className="welcome-message">
              <FaRobot size={60} color="#667eea" />
              <h2>Welcome to Real Estate AI</h2>
              <p>Start a conversation or upload a property image to get started</p>

              <div className="quick-actions">
                <h3>Quick Actions:</h3>
                <button onClick={() => setInputText("What are the best neighborhoods in Abu Dhabi?")}>
                  🏘️ Best Neighborhoods
                </button>
                <button onClick={() => setInputText("How do I evaluate property prices?")}>
                  💰 Property Evaluation
                </button>
                <button onClick={() => setInputText("Tell me about investment opportunities")}>
                  📈 Investment Tips
                </button>
              </div>
            </div>
          )}

          {messages.map((msg, index) => (
            <div key={index} className={`message ${msg.role}`}>
              <div className="message-content">
                {msg.image && <img src={msg.image} alt="Uploaded" className="message-image" />}
                <p>{msg.content}</p>
                {msg.responseTime && (
                  <div className="message-meta">
                    <FaTachometerAlt size={12} />
                    <span>{msg.responseTime.toFixed(2)}s</span>
                  </div>
                )}
              </div>
            </div>
          ))}

          {isLoading && (
            <div className="message assistant">
              <div className="message-content">
                <div className="typing-indicator">
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        <div className="input-container">
          <input
            type="text"
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleSendMessage()}
            placeholder="Ask about properties, prices, locations..."
            disabled={isLoading}
          />
          <button onClick={handleSendMessage} disabled={isLoading || (!inputText.trim() && !selectedImage)}>
            <FaPaperPlane />
          </button>
        </div>
      </div>
    </div>
  );
}

export default ChatPage;
