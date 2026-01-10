# Streamlit Version - Real Estate AI Chatbot

Simple and quick-to-deploy Streamlit interface for the Real Estate AI assistant.

## ⚡ Quick Start

### 1. Install Dependencies

```bash
cd streamlit-version
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Ensure Ollama is Running

```bash
# Check Ollama service
ollama list

# If models not installed:
ollama pull llama3.1:8b
ollama pull llava:7b
```

### 3. Run Application

```bash
streamlit run app.py
```

Access at: **http://localhost:8501**

## 🎯 Features

- ✅ Text chat with Llama 3.1 8B
- ✅ Image analysis with LLaVA 7B
- ✅ Voice responses (TTS)
- ✅ Simple, intuitive interface
- ✅ Real-time model switching

## 🔧 Configuration

Edit `app.py` to customize:
- Model names
- Voice speed
- UI theme
- Temperature/parameters

## 📝 Notes

- Requires active Ollama service
- Voice requires internet for Google TTS
- Best for demos and quick testing
- Not optimized for production scale

## 🚀 Next Steps

For production deployment, use the **React version** with separate backend/frontend.
