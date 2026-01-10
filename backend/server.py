from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import ollama
from gtts import gTTS
import speech_recognition as sr
from PIL import Image
from io import BytesIO
import tempfile
import os
import uuid

app = FastAPI()

# Enable CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/chat")
async def chat(message: str = Form(...)):
    """Handle text chat"""
    try:
        response = ollama.chat(
            model='llama3.1:8b',
            messages=[
                {'role': 'system', 'content': 'You are a professional Abu Dhabi real estate assistant helping with property searches, prices, locations, and advice.'},
                {'role': 'user', 'content': message}
            ]
        )
        return {"response": response['message']['content']}
    except Exception as e:
        return {"error": str(e)}

@app.post("/api/chat-with-image")
async def chat_with_image(
    message: str = Form(...),
    image: UploadFile = File(...)
):
    """Handle chat with image analysis"""
    try:
        # Read and process image
        img_bytes = await image.read()

        response = ollama.chat(
            model='llava:7b',
            messages=[
                {
                    'role': 'user',
                    'content': f'You are a professional Abu Dhabi real estate assistant. Analyze this property image and answer: {message}',
                    'images': [img_bytes]
                }
            ]
        )
        return {"response": response['message']['content']}
    except Exception as e:
        return {"error": str(e)}

@app.post("/api/transcribe")
async def transcribe_audio(audio: UploadFile = File(...)):
    """Transcribe audio to text"""
    try:
        # Save audio temporarily
        audio_bytes = await audio.read()
        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp_file:
            tmp_file.write(audio_bytes)
            tmp_path = tmp_file.name

        # Transcribe
        recognizer = sr.Recognizer()
        with sr.AudioFile(tmp_path) as source:
            audio_data = recognizer.record(source)
            text = recognizer.recognize_google(audio_data)

        os.remove(tmp_path)
        return {"text": text}
    except Exception as e:
        return {"error": str(e)}

@app.post("/api/text-to-speech")
async def text_to_speech(text: str = Form(...)):
    """Convert text to speech - optimized for speed"""
    try:
        # Truncate long responses for faster TTS
        max_chars = 500
        if len(text) > max_chars:
            text = text[:max_chars] + "..."

        filename = f"{uuid.uuid4()}.mp3"
        filepath = f"/tmp/{filename}"

        # Use gTTS with optimized settings
        tts = gTTS(text=text, lang='en', slow=False, tld='com')
        tts.save(filepath)

        return {"audio_url": f"/api/audio/{filename}"}
    except Exception as e:
        return {"error": str(e)}

@app.get("/api/audio/{filename}")
async def get_audio(filename: str):
    """Serve audio files"""
    filepath = f"/tmp/{filename}"
    return FileResponse(filepath, media_type="audio/mpeg")

@app.get("/")
async def root():
    return {"message": "Real Estate Chatbot API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
