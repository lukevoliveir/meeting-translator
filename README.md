# Meeting Real-Time Translator

Real-time meeting translation with a React web UI and a FastAPI backend.
Works with any video call platform (Zoom, Meet, Teams, etc.) via system audio capture.

## Requirements

- Python 3.10+
- Node 18+
- [BlackHole](https://existential.audio/blackhole/) (macOS loopback audio driver)

## Quick Start

### 1. Backend

```bash
cd backend
pip install -r requirements.txt
python main.py
# API running at http://localhost:8000
```

### 2. Frontend

```bash
cd frontend
npm install
npm run dev
# App running at http://localhost:5173
```

Open **http://localhost:5173** in your browser.

## Usage Flow

1. **Select language** — choose the subtitle language
2. **Speaker profile** *(optional)* — paste YouTube URLs to build a vocabulary profile
3. **Live overlay** — translated captions appear in real time from system audio
4. **Session summary** — phrase count, duration, and recent captions on exit

## Architecture

```
Browser (React)  ←──WebSocket──→  FastAPI backend
                                    ├── AudioCapture (loopback)
                                    ├── WhisperTranscriber
                                    ├── Translator (GoogleTranslator)
                                    └── ProfileManager
```

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/languages` | Supported languages |
| POST | `/api/speaker-profiles` | Create speaker profile from YouTube URLs |
| GET | `/api/speaker-profiles` | List saved profiles |
| GET | `/api/session/{id}` | Session summary |
| WS | `/ws/transcribe/{id}` | Real-time caption stream |
| GET | `/health` | Health check |
