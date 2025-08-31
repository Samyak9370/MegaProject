import os
import tempfile
import speech_recognition as sr
from pydub import AudioSegment
from fastapi import UploadFile, HTTPException
from typing import Tuple
import numpy as np
import librosa
from ..core.config import settings

class SpeechService:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        
    async def process_audio(self, audio_file: UploadFile) -> Tuple[str, float]:
        """Process uploaded audio file and return transcript and duration."""
        try:
            # Save the uploaded file temporarily
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_audio:
                temp_audio.write(await audio_file.read())
                temp_audio_path = temp_audio.name
            
            # Convert to WAV if needed
            if audio_file.content_type != "audio/wav":
                temp_audio_path = self._convert_to_wav(temp_audio_path)
            
            # Get audio duration
            duration = self._get_audio_duration(temp_audio_path)
            
            # Transcribe audio
            transcript = await self._transcribe_audio(temp_audio_path)
            
            # Clean up temporary files
            os.unlink(temp_audio_path)
            if temp_audio_path != temp_audio.name:
                os.unlink(temp_audio.name)
                
            return transcript, duration
            
        except Exception as e:
            # Clean up in case of error
            if 'temp_audio_path' in locals() and os.path.exists(temp_audio_path):
                os.unlink(temp_audio_path)
            if 'temp_audio' in locals() and os.path.exists(temp_audio.name):
                os.unlink(temp_audio.name)
            raise HTTPException(status_code=500, detail=f"Audio processing failed: {str(e)}")
    
    def _convert_to_wav(self, input_path: str) -> str:
        """Convert audio file to WAV format."""
        output_path = f"{os.path.splitext(input_path)[0]}.wav"
        try:
            audio = AudioSegment.from_file(input_path)
            audio = audio.set_frame_rate(16000).set_channels(1)
            audio.export(output_path, format="wav")
            return output_path
        except Exception as e:
            if os.path.exists(output_path):
                os.unlink(output_path)
            raise Exception(f"Audio conversion failed: {str(e)}")
    
    def _get_audio_duration(self, audio_path: str) -> float:
        """Get duration of audio file in seconds."""
        try:
            y, sr = librosa.load(audio_path, sr=None)
            return float(len(y)) / float(sr)
        except Exception as e:
            raise Exception(f"Failed to get audio duration: {str(e)}")
    
    async def _transcribe_audio(self, audio_path: str) -> str:
        """Transcribe audio file to text using Google Speech Recognition."""
        try:
            with sr.AudioFile(audio_path) as source:
                audio_data = self.recognizer.record(source)
                text = self.recognizer.recognize_google(audio_data)
                return text
        except sr.UnknownValueError:
            raise Exception("Could not understand audio")
        except sr.RequestError as e:
            raise Exception(f"Could not request results; {str(e)}")
        except Exception as e:
            raise Exception(f"Transcription failed: {str(e)}")

# Create a singleton instance
speech_service = SpeechService()
