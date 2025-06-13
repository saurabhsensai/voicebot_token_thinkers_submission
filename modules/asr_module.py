import whisper
import torch
import librosa
import numpy as np
import os
from typing import Optional
import yaml

class WhisperASR:
    def __init__(self, config_path: str = "config/config.yaml"):
        """Initialize the Whisper ASR model with configuration."""
        with open(config_path, 'r') as file:
            self.config = yaml.safe_load(file)
        
        self.model_name = self.config.get('whisper_model', 'base')
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model = whisper.load_model(self.model_name).to(self.device)
        
    def load_audio(self, audio_path: str) -> np.ndarray:
        """Load audio file and ensure correct sampling rate."""
        audio, sr = librosa.load(audio_path, sr=16000)  # Whisper expects 16kHz
        return audio

    def transcribe(self, audio_path: str, language: Optional[str] = None) -> str:
        """Transcribe audio to English text."""
        try:
            audio = self.load_audio(audio_path)
            # Whisper automatically detects language if not specified
            result = self.model.transcribe(
                audio,
                language=language,
                task="translate"  # Translate to English
            )
            return result["text"].strip()
        except Exception as e:
            return f"Error transcribing audio: {str(e)}"

    def process_batch(self, audio_files: list) -> list:
        """Process multiple audio files and return transcriptions."""
        transcriptions = []
        for audio_path in audio_files:
            transcription = self.transcribe(audio_path)
            transcriptions.append(transcription)
        return transcriptions