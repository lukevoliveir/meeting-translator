# Meeting Real-Time Translator

Real-time meeting translation with a React web UI and a FastAPI backend.
Works with any video call platform (Zoom, Meet, Teams, etc.) via system audio capture.

## Requirements

- Python 3.10+
- Node 18+
- An audio loopback source (see [Audio Configuration](#audio-configuration) below)

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

## Audio Configuration

The app captures system audio (output from Zoom, Meet, Teams, etc.) using a loopback device.
It automatically detects the best available option in this priority order:

### Option 1 — WASAPI Native Loopback (Windows, recommended)

No driver installation required. Works on any Windows 10/11 system.
Just install the extra Python dependency:

```bash
pip install pyaudiowpatch
```

The app will automatically capture audio from your default output device.

### Option 2 — VB-Audio Virtual Cable (Windows/macOS, free)

A lightweight virtual audio driver that creates a loopback device.

1. Download from **<https://vb-audio.com/Cable/>**
2. Install and restart your computer
3. In your video call app, set the audio output to **CABLE Input**
4. The app will detect **CABLE Output** automatically

### Option 3 — Stereo Mix (Windows, legacy)

Some Realtek sound cards include Stereo Mix. Enable it via:

> Control Panel → Sound → Recording tab → right-click → *Show Disabled Devices* → enable **Stereo Mix**

### Option 4 — BlackHole (macOS)

Virtual audio driver for macOS loopback capture.

1. Download from **<https://existential.audio/blackhole/>**
2. Follow the multi-output device setup guide on their site

### Manual device override

Force a specific device by name using an environment variable:

```bash
# Windows
set AUDIO_LOOPBACK_DEVICE=CABLE Output

# macOS / Linux
export AUDIO_LOOPBACK_DEVICE="BlackHole 2ch"
```

### Diagnostic endpoint

`GET /audio/devices` returns the active device, all detected candidates, and download links.
Useful for debugging when the prerequisites screen shows no loopback device.

---

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/languages` | Supported languages |
| POST | `/api/speaker-profiles` | Create speaker profile from YouTube URLs |
| GET | `/api/speaker-profiles` | List saved profiles |
| GET | `/api/session/{id}` | Session summary |
| WS | `/ws/transcribe/{id}` | Real-time caption stream |
| GET | `/health` | Health check |
| GET | `/api/system/check` | OS info and loopback device status |
| GET | `/audio/devices` | Diagnostic: all detected loopback candidates |
| PUT | `/audio/device` | Switch loopback device at runtime (`{"name": "..."}`) |
