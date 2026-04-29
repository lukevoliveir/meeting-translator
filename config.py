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

# Glossary profile for term protection (tech, finance, legal, none)
GLOSSARY_PROFILE = "tech"

# Supported languages: (code, flag_emoji, display_name)
SUPPORTED_LANGUAGES = [
    ("pt", "🇧🇷", "Português"),
    ("en", "🇺🇸", "English"),
    ("es", "🇪🇸", "Español"),
    ("fr", "🇫🇷", "Français"),
    ("de", "🇩🇪", "Deutsch"),
    ("it", "🇮🇹", "Italiano"),
    ("ja", "🇯🇵", "日本語"),
    ("zh", "🇨🇳", "中文"),
    ("ko", "🇰🇷", "한국어"),
    ("ar", "🇸🇦", "العربية"),
]
