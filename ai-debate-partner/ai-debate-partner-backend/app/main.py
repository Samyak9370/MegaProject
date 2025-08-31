import asyncio
import base64
import json
import logging
import os
import subprocess
import uuid
from datetime import datetime
from typing import Dict, Any, List

import nltk
import speech_recognition as sr
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from nltk.tokenize import word_tokenize, sent_tokenize
from pydub import AudioSegment
from pydub.utils import which

try:
    from textblob import TextBlob
except ImportError:
    TextBlob = None
    print("Warning: TextBlob not installed. Some features may be limited.")

# Configure pydub
AudioSegment.ffmpeg = r"C:\ffmpeg\bin\ffmpeg.exe"
AudioSegment.ffprobe = r"C:\ffmpeg\bin\ffprobe.exe"

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Download NLTK data
try:
    nltk.download('punkt', quiet=True)
    nltk.download('averaged_perceptron_tagger', quiet=True)
except Exception as e:
    logger.warning(f"Failed to download NLTK data: {e}")

# Set FFmpeg paths
ffmpeg_path = r"C:\ffmpeg\bin\ffmpeg.exe"
ffprobe_path = r"C:\ffmpeg\bin\ffprobe.exe"

# Verify FFmpeg
if not os.path.exists(ffmpeg_path):
    logger.error("FFmpeg not found at C:\\ffmpeg\\bin\\ffmpeg.exe. Please install FFmpeg.")
else:
    try:
        result = subprocess.run([ffmpeg_path, "-version"], capture_output=True, text=True, check=True)
        logger.debug(f"FFmpeg version: {result.stdout.splitlines()[0]}")
    except Exception as e:
        logger.error(f"FFmpeg check failed: {e}")

if not os.path.exists(ffprobe_path):
    logger.error("FFprobe not found at C:\\ffmpeg\\bin\\ffprobe.exe. Please install FFmpeg.")
else:
    try:
        result = subprocess.run([ffprobe_path, "-version"], capture_output=True, text=True, check=True)
        logger.debug(f"FFprobe version: {result.stdout.splitlines()[0]}")
    except Exception as e:
        logger.error(f"FFprobe check failed: {e}")

# Initialize FastAPI app
app = FastAPI(title="AI Debate Analyzer")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage (replace with SQLite in production)
session_history: Dict[str, List[Dict]] = {}

# Connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.client_data: Dict[str, Dict[str, Any]] = {}
        self.recognizer = sr.Recognizer()
        self.recognizer.dynamic_energy_threshold = True
        self.recognizer.pause_threshold = 0.8

    async def connect(self, client_id: str, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[client_id] = websocket
        self.client_data[client_id] = {
            "connected_at": datetime.utcnow(),
            "transcript": "",
            "audio_chunks": [],
            "metrics": {
                "word_count": 0,
                "unique_words": 0,
                "vocabulary_richness": 0,
                "avg_word_length": 0,
                "sentence_count": 0,
                "filler_word_count": 0,
                "grammar_errors": 0,
                "hesitation_count": 0,
                "speaking_rate": 0,
                "overall_score": 0,
                "clarity_score": 0,
                "confidence_score": 0,
                "fluency_score": 0
            },
            "feedback": {
                "strengths": [],
                "areas_for_improvement": [],
                "suggestions": []
            }
        }
        if client_id not in session_history:
            session_history[client_id] = []
        logger.info(f"Client {client_id} connected")

    def disconnect(self, client_id: str):
        if client_id in self.active_connections:
            del self.active_connections[client_id]
        if client_id in self.client_data:
            del self.client_data[client_id]
        logger.info(f"Client {client_id} disconnected")

manager = ConnectionManager()

# AI-based reply system (placeholder)
async def generate_ai_reply(text: str) -> str:
    if TextBlob:
        blob = TextBlob(text)
        sentiment = blob.sentiment.polarity
        if sentiment > 0.1:
            return "Great point! Consider adding specific examples to strengthen your argument."
        elif sentiment < -0.1:
            return "Strong perspective, but try a more neutral tone for broader appeal."
        else:
            return "Solid argument. Vary sentence structure for better engagement."
    return "AI reply not available due to missing TextBlob."

# Analyze speech
async def analyze_speech(text: str, audio_duration: float, audio_data: bytes) -> Dict:
    words = word_tokenize(text.lower())
    sentences = sent_tokenize(text)
    
    # Metrics
    word_count = len(words)
    unique_words = len(set(words))
    vocabulary_richness = unique_words / (word_count or 1)
    avg_word_length = sum(len(word) for word in words) / (word_count or 1)
    sentence_count = len(sentences)
    
    # Filler words
    filler_words = ['um', 'uh', 'like', 'you know', 'so']
    filler_word_count = sum(1 for word in words if word in filler_words)
    
    # Grammar errors
    grammar_errors = 0
    if TextBlob:
        blob = TextBlob(text)
        grammar_errors = len([word for word, pos in blob.tags if pos == 'NN' and word.endswith('ing')])
    
    # Hesitation (placeholder)
    hesitation_count = max(0, int(audio_duration / 2) - 1)
    
    # Speaking rate
    speaking_rate = word_count / (audio_duration / 60) if audio_duration > 0 else 0
    
    # Voice analysis
    clarity_score = min(10, len(audio_data) / 200) if audio_data else 5
    confidence_score = 8 if 120 < speaking_rate < 180 else 6
    fluency_score = 8 if filler_word_count / (word_count or 1) < 0.1 else 6
    overall_score = (clarity_score + confidence_score + fluency_score + (1 - grammar_errors / (sentence_count or 1)) * 10) / 4
    
    # Feedback
    strengths = []
    areas_for_improvement = []
    suggestions = []
    
    if grammar_errors == 0:
        strengths.append("Excellent grammar and sentence structure.")
    else:
        areas_for_improvement.append(f"Found {grammar_errors} potential grammar issues.")
        suggestions.append("Review verb forms and sentence complexity.")
    
    if vocabulary_richness > 0.7:
        strengths.append("Strong vocabulary diversity.")
    else:
        areas_for_improvement.append("Limited vocabulary diversity.")
        suggestions.append("Incorporate more varied words.")
    
    if filler_word_count == 0:
        strengths.append("No filler words detected.")
    else:
        areas_for_improvement.append(f"Detected {filler_word_count} filler words.")
        suggestions.append("Practice pausing instead of using filler words.")
    
    if confidence_score > 7:
        strengths.append("Confident delivery.")
    else:
        areas_for_improvement.append("Speaking rate could be more consistent.")
        suggestions.append("Aim for 120-180 words per minute.")
    
    # AI reply
    ai_reply = await generate_ai_reply(text)
    suggestions.append(ai_reply)
    
    return {
        "metrics": {
            "word_count": word_count,
            "unique_words": unique_words,
            "vocabulary_richness": vocabulary_richness,
            "avg_word_length": avg_word_length,
            "sentence_count": sentence_count,
            "filler_word_count": filler_word_count,
            "grammar_errors": grammar_errors,
            "hesitation_count": hesitation_count,
            "speaking_rate": speaking_rate,
            "overall_score": overall_score,
            "clarity_score": clarity_score,
            "confidence_score": confidence_score,
            "fluency_score": fluency_score
        },
        "feedback": {
            "strengths": strengths,
            "areas_for_improvement": areas_for_improvement,
            "suggestions": suggestions
        }
    }

# WebSocket endpoint
@app.websocket("/ws/debate/{session_id}")
async def debate_websocket(websocket: WebSocket, session_id: str):
    await manager.connect(session_id, websocket)
    logger.info(f"New debate session started: {session_id}")
    
    temp_dir = r"C:\Users\mukun\temp"
    debug_dir = r"C:\Users\mukun\temp\debug"
    for directory in [temp_dir, debug_dir]:
        if not os.path.exists(directory):
            os.makedirs(directory)
            logger.debug(f"Created directory: {directory}")
    
    try:
        while True:
            data = await websocket.receive_text()
            try:
                message = json.loads(data)
                message_type = message.get("type")
                
                if message_type == "audio_chunk":
                    try:
                        base64_string = message["data"]
                        mime_type = message.get("mime_type", "audio/webm;codecs=opus")
                        logger.debug(f"Received audio chunk, base64 length: {len(base64_string)}, MIME type: {mime_type}")
                        
                        # Save base64 for debugging
                        debug_base64_path = os.path.join(debug_dir, f"base64_{uuid.uuid4()}.txt")
                        with open(debug_base64_path, "w") as debug_file:
                            debug_file.write(base64_string)
                        
                        # Decode base64
                        audio_data = base64.b64decode(base64_string)
                        if not audio_data:
                            raise ValueError("Empty audio data")
                        
                        audio_duration = message.get("duration_seconds", 0)
                        extension = "webm" if "webm" in mime_type.lower() else "ogg"
                        temp_audio_path = os.path.join(temp_dir, f"audio_{uuid.uuid4()}.{extension}")
                        
                        # Save audio
                        with open(temp_audio_path, "wb") as temp_audio_file:
                            temp_audio_file.write(audio_data)
                            temp_audio_file.flush()
                            os.fsync(temp_audio_file.fileno())
                        file_size = os.path.getsize(temp_audio_path)
                        logger.debug(f"Saved audio: {temp_audio_path}, size: {file_size} bytes")
                        
                        if file_size < 1000:
                            raise ValueError(f"Audio file too small: {file_size} bytes")
                        
                        # Save debug copy
                        debug_audio_path = os.path.join(debug_dir, f"debug_audio_{uuid.uuid4()}.{extension}")
                        with open(debug_audio_path, "wb") as debug_audio_file:
                            debug_audio_file.write(audio_data)
                        
                        # Validate with ffprobe
                        try:
                            result = subprocess.run(
                                [ffprobe_path, "-v", "error", "-show_streams", "-print_format", "json", temp_audio_path],
                                capture_output=True,
                                text=True,
                                check=True
                            )
                            ffprobe_output = json.loads(result.stdout)
                            if not ffprobe_output.get("streams"):
                                raise ValueError("No audio streams found")
                            logger.debug(f"FFprobe validation: {ffprobe_output}")
                        except Exception as e:
                            logger.error(f"FFprobe validation failed: {e}")
                            raise Exception(f"Invalid audio file: {e}")
                        
                        # Convert to WAV
                        temp_wav_path = os.path.join(temp_dir, f"audio_{uuid.uuid4()}.wav")
                        try:
                            result = subprocess.run(
                                [ffmpeg_path, "-f", extension, "-i", temp_audio_path, "-acodec", "pcm_s16le", "-ar", "16000", temp_wav_path],
                                capture_output=True,
                                text=True,
                                check=True
                            )
                            logger.debug(f"FFmpeg conversion: stdout={result.stdout}, stderr={result.stderr}")
                        except subprocess.CalledProcessError as e:
                            logger.error(f"FFmpeg conversion failed: stdout={e.stdout}, stderr={e.stderr}")
                            raise Exception(f"FFmpeg conversion failed: {e.stderr}")
                        
                        wav_size = os.path.getsize(temp_wav_path)
                        logger.debug(f"Exported WAV: {temp_wav_path}, size: {wav_size} bytes")
                        
                        if wav_size == 0:
                            raise ValueError("WAV file is empty")
                        
                        # Speech recognition
                        with sr.AudioFile(temp_wav_path) as source:
                            audio = manager.recognizer.record(source)
                            try:
                                text = manager.recognizer.recognize_google(audio)
                                logger.debug(f"Transcribed text: {text}")
                                
                                manager.client_data[session_id]["transcript"] += " " + text
                                analysis = await analyze_speech(text, audio_duration, audio_data)
                                
                                manager.client_data[session_id]["metrics"] = analysis["metrics"]
                                manager.client_data[session_id]["feedback"] = analysis["feedback"]
                                
                                await websocket.send_json({
                                    "type": "analysis_update",
                                    "timestamp": datetime.utcnow().isoformat(),
                                    "transcript": text,
                                    "full_transcript": manager.client_data[session_id]["transcript"],
                                    "metrics": analysis["metrics"],
                                    "feedback": analysis["feedback"],
                                    "ai_reply": analysis["feedback"]["suggestions"][-1]
                                })
                            except sr.UnknownValueError:
                                await websocket.send_json({
                                    "type": "warning",
                                    "message": "Could not understand audio.",
                                    "timestamp": datetime.utcnow().isoformat()
                                })
                            except sr.RequestError as e:
                                await websocket.send_json({
                                    "type": "error",
                                    "message": f"Speech recognition error: {e}",
                                    "timestamp": datetime.utcnow().isoformat()
                                })
                    except Exception as e:
                        logger.error(f"Error in speech recognition: {e}")
                        await websocket.send_json({
                            "type": "error",
                            "message": f"Error processing speech: {e}",
                            "timestamp": datetime.utcnow().isoformat()
                        })
                    finally:
                        if os.path.exists(temp_audio_path):
                            os.unlink(temp_audio_path)
                        if 'temp_wav_path' in locals() and os.path.exists(temp_wav_path):
                            os.unlink(temp_wav_path)
                
                elif message_type == "session_end":
                    session_duration = message.get("session_duration_seconds", 0) / 60
                    session_data = {
                        "session_id": session_id,
                        "timestamp": datetime.utcnow().isoformat(),
                        "duration_minutes": session_duration,
                        "total_words": manager.client_data[session_id]["metrics"]["word_count"],
                        "avg_words_per_minute": manager.client_data[session_id]["metrics"]["speaking_rate"],
                        "filler_word_rate": manager.client_data[session_id]["metrics"]["filler_word_count"] / (manager.client_data[session_id]["metrics"]["word_count"] or 1),
                        "vocabulary_richness": manager.client_data[session_id]["metrics"]["vocabulary_richness"],
                        "overall_score": manager.client_data[session_id]["metrics"]["overall_score"],
                        "clarity_score": manager.client_data[session_id]["metrics"]["clarity_score"],
                        "confidence_score": manager.client_data[session_id]["metrics"]["confidence_score"],
                        "fluency_score": manager.client_data[session_id]["metrics"]["fluency_score"],
                        "key_takeaways": manager.client_data[session_id]["feedback"]["suggestions"],
                        "full_transcript": manager.client_data[session_id]["transcript"]
                    }
                    session_history[session_id].append(session_data)
                    await websocket.send_json({
                        "type": "session_summary",
                        "message": "Session ended",
                        "timestamp": datetime.utcnow().isoformat(),
                        **session_data
                    })
                
                elif message_type == "connection_init":
                    await websocket.send_json({
                        "type": "connection_ack",
                        "message": "Connection established",
                        "timestamp": datetime.utcnow().isoformat()
                    })
                
                elif message_type == "ping":
                    await websocket.send_json({
                        "type": "pong",
                        "timestamp": datetime.utcnow().isoformat()
                    })
                
            except json.JSONDecodeError:
                await websocket.send_json({
                    "type": "error",
                    "message": "Invalid JSON format",
                    "timestamp": datetime.utcnow().isoformat()
                })
    except WebSocketDisconnect:
        manager.disconnect(session_id)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(session_id)

# Session history endpoint
@app.get("/history/{session_id}")
async def get_session_history(session_id: str):
    return session_history.get(session_id, [])

# Root endpoint
@app.get("/")
async def root():
    return {"message": "AI Debate Analyzer API is running", "docs": "/docs"}

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
