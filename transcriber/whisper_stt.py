"""Speech-to-text transcription using OpenAI's Whisper model."""

from typing import Tuple

import librosa
import numpy as np
import whisper

from config import SAMPLE_RATE, SILENCE_THRESHOLD, WHISPER_MODEL


class WhisperTranscriber:
    """Transcribes audio chunks using OpenAI's Whisper model."""

    def __init__(self):
        """Initialize Whisper model. This loads the model from disk or downloads it."""
        print(f"Loading Whisper model '{WHISPER_MODEL}'...")
        self.model = whisper.load_model(WHISPER_MODEL)
        print("Whisper model loaded successfully")

    def is_silence(self, audio_chunk: np.ndarray) -> bool:
        """
        Detect if an audio chunk is primarily silence.

        Args:
            audio_chunk: Audio data as numpy float32 array.

        Returns:
            True if the chunk is silent, False otherwise.
        """
        rms = np.sqrt(np.mean(audio_chunk**2))
        return rms < SILENCE_THRESHOLD

    def transcribe(self, audio_chunk: np.ndarray) -> Tuple[str, str]:
        """
        Transcribe an audio chunk and detect its language.

        Args:
            audio_chunk: Audio data as numpy float32 array with shape (SAMPLE_RATE * CHUNK_SECONDS,).

        Returns:
            Tuple of (transcribed_text, language_code). Language code is ISO 639-1 format (e.g., 'pt', 'en').
        """
        if self.is_silence(audio_chunk):
            return "", "silent"

        try:
            # Whisper expects audio in float32 format with sample rate of 16000
            result = self.model.transcribe(
                audio_chunk,
                language=None,  # Auto-detect language
                fp16=False,  # Use CPU-friendly fp32 precision
            )

            text = result.get("text", "").strip()
            language = result.get("language", "unknown")

            return text, language

        except Exception as e:
            print(f"Error during transcription: {e}")
            return "", "error"

    def get_model_info(self) -> dict:
        """
        Get information about the loaded model.

        Returns:
            Dictionary with model information.
        """
        return {
            "model": WHISPER_MODEL,
            "sample_rate": SAMPLE_RATE,
        }
