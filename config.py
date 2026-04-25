"""Configuration constants for the Meeting Real-Time Translator."""

# Target language for translated captions (ISO 639-1 code)
TARGET_LANG = "pt"

# Whisper model size: tiny, base, small, medium, large
# Larger models are more accurate but slower and require more memory
WHISPER_MODEL = "base"

# Audio chunk duration in seconds
CHUNK_SECONDS = 3

# Sample rate in Hz (16kHz is standard for speech recognition)
SAMPLE_RATE = 16000

# Silence detection threshold (RMS level below this is considered silence)
SILENCE_THRESHOLD = 0.01
