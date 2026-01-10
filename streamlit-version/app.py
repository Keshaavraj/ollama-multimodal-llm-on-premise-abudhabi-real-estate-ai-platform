import streamlit as st
import ollama
from io import BytesIO
from PIL import Image
import speech_recognition as sr
from gtts import gTTS
from audio_recorder_streamlit import audio_recorder
import tempfile
import os

st.set_page_config(page_title="Real Estate Chatbot", page_icon="🏠")

st.title("🏠 Real Estate Chatbot")
st.markdown("Ask me anything - Type, Speak Live, Upload Audio/Images!")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Sidebar
with st.sidebar:
    st.header("📤 Input Options")

    # Image upload
    st.subheader("🖼️ Property Image")
    uploaded_file = st.file_uploader("Upload property image", type=['png', 'jpg', 'jpeg'])
    if uploaded_file:
        st.image(uploaded_file, caption="Uploaded Image", use_container_width=True)

    # Real-time voice recording
    st.subheader("🎤 Live Voice Recording")
    st.write("Click to record:")
    audio_bytes = audio_recorder(pause_threshold=2.0, sample_rate=41000)

    # Audio file upload
    st.subheader("📁 Upload Audio File")
    uploaded_audio = st.file_uploader("Upload audio file", type=['wav', 'mp3', 'm4a', 'ogg'])

    # Settings
    st.subheader("⚙️ Settings")
    enable_voice_response = st.checkbox("Enable Voice Responses", value=True)
    voice_speed = st.slider("Voice Speed", 0.5, 2.0, 1.0, 0.1)

# Function to convert speech to text from bytes
def speech_to_text_from_bytes(audio_bytes):
    recognizer = sr.Recognizer()
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp_file:
            tmp_file.write(audio_bytes)
            tmp_path = tmp_file.name

        with sr.AudioFile(tmp_path) as source:
            audio_data = recognizer.record(source)
            text = recognizer.recognize_google(audio_data)

        os.remove(tmp_path)
        return text
    except sr.UnknownValueError:
        return "Sorry, I could not understand the audio"
    except Exception as e:
        return f"Error: {str(e)}"

# Function to convert speech to text from file
def speech_to_text_from_file(audio_file):
    recognizer = sr.Recognizer()
    try:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp_file:
            tmp_file.write(audio_file.read())
            tmp_path = tmp_file.name

        # Convert to WAV if needed using pydub
        from pydub import AudioSegment
        audio = AudioSegment.from_file(tmp_path)
        wav_path = tmp_path.replace(tmp_path.split('.')[-1], 'wav')
        audio.export(wav_path, format='wav')

        with sr.AudioFile(wav_path) as source:
            audio_data = recognizer.record(source)
            text = recognizer.recognize_google(audio_data)

        os.remove(tmp_path)
        if wav_path != tmp_path:
            os.remove(wav_path)

        return text
    except sr.UnknownValueError:
        return "Sorry, I could not understand the audio"
    except Exception as e:
        return f"Error: {str(e)}"

# Function to convert text to speech
def text_to_speech(text, slow=False):
    try:
        tts = gTTS(text=text, lang='en', slow=slow)
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as fp:
            tts.save(fp.name)
            return fp.name
    except Exception as e:
        st.error(f"TTS Error: {str(e)}")
        return None

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "image" in message and message["image"]:
            st.image(message["image"], width=300)
        if "audio" in message and message["audio"]:
            st.audio(message["audio"])

# Process real-time voice recording
transcribed_text = None
if audio_bytes:
    with st.spinner("🎤 Transcribing your voice..."):
        transcribed_text = speech_to_text_from_bytes(audio_bytes)
        if transcribed_text and not transcribed_text.startswith("Error"):
            st.success(f"🎤 You said: **{transcribed_text}**")
        else:
            st.warning(transcribed_text)

# Process uploaded audio file
if uploaded_audio:
    with st.spinner("🎵 Processing uploaded audio..."):
        transcribed_from_file = speech_to_text_from_file(uploaded_audio)
        if transcribed_from_file and not transcribed_from_file.startswith("Error"):
            st.success(f"🎵 Transcribed from file: **{transcribed_from_file}**")
            transcribed_text = transcribed_from_file
        else:
            st.warning(transcribed_from_file)

# Text input
text_prompt = st.chat_input("Type your question here...")

# Determine which prompt to use
prompt = None
if transcribed_text and not transcribed_text.startswith("Error") and not transcribed_text.startswith("Sorry"):
    prompt = transcribed_text
elif text_prompt:
    prompt = text_prompt

# Process the prompt
if prompt:
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Get bot response
    with st.chat_message("assistant"):
        with st.spinner("🤔 Thinking..."):
            # Check if there's an uploaded image
            if uploaded_file is not None:
                # Use llava for image analysis
                image = Image.open(uploaded_file)
                buffered = BytesIO()
                image.save(buffered, format="PNG")
                img_bytes = buffered.getvalue()

                response = ollama.chat(
                    model='llava:7b',
                    messages=[
                        {
                            'role': 'user',
                            'content': f'You are a professional Abu Dhabi real estate assistant. Analyze this property image and answer: {prompt}',
                            'images': [img_bytes]
                        }
                    ]
                )
                bot_response = response['message']['content']
            else:
                # Use llama3.1 for text-only chat
                response = ollama.chat(
                    model='llama3.1:8b',
                    messages=[
                        {'role': 'system', 'content': 'You are a professional Abu Dhabi real estate assistant helping with property searches, prices, locations, and advice. Keep responses concise and clear.'},
                        {'role': 'user', 'content': prompt}
                    ]
                )
                bot_response = response['message']['content']

            # Display text response
            st.markdown(bot_response)

            # Generate audio response if enabled
            audio_path = None
            if enable_voice_response:
                with st.spinner("🔊 Generating voice response..."):
                    use_slow = voice_speed < 1.0
                    audio_path = text_to_speech(bot_response, slow=use_slow)
                    if audio_path:
                        st.audio(audio_path)

            # Store in chat history
            message_data = {
                "role": "assistant",
                "content": bot_response,
                "audio": audio_path if enable_voice_response else None,
                "image": None
            }
            if uploaded_file:
                message_data["image"] = uploaded_file

            st.session_state.messages.append(message_data)

# Add clear chat button
if st.sidebar.button("🗑️ Clear Chat History"):
    st.session_state.messages = []
    st.rerun()

