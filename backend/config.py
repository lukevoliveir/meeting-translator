import os

# Audio
SAMPLE_RATE = 16000
CHUNK_SECONDS = 5
SILENCE_THRESHOLD = 0.005

# Whisper
WHISPER_MODEL = "small"

# Translation
TRANSLATION_PROVIDER = "google"

# Glossary
GLOSSARY_PROFILES = {
    "tech": ["pipeline", "deploy", "sprint", "backend", "frontend", "API", "bug"],
    "finance": ["revenue", "churn", "ARR", "MRR", "runway", "burn rate"],
    "legal": ["compliance", "liability", "NDA", "clause", "indemnity"],
}

# Storage
PROFILES_DIR = os.path.expanduser("~/.meeting-translator/profiles")
CACHE_DIR = os.path.expanduser("~/.meeting-translator/cache")

SUPPORTED_LANGUAGES = [
    {"code": "pt", "flag": "🇧🇷", "name": "Português"},
    {"code": "en", "flag": "🇺🇸", "name": "English"},
    {"code": "es", "flag": "🇪🇸", "name": "Español"},
    {"code": "fr", "flag": "🇫🇷", "name": "Français"},
    {"code": "de", "flag": "🇩🇪", "name": "Deutsch"},
    {"code": "it", "flag": "🇮🇹", "name": "Italiano"},
    {"code": "ja", "flag": "🇯🇵", "name": "日本語"},
    {"code": "zh", "flag": "🇨🇳", "name": "中文"},
    {"code": "ko", "flag": "🇰🇷", "name": "한국어"},
    {"code": "ar", "flag": "🇸🇦", "name": "العربية"},
]

os.makedirs(PROFILES_DIR, exist_ok=True)
os.makedirs(CACHE_DIR, exist_ok=True)
