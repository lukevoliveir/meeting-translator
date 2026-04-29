import asyncio
import re
import sys
import os
from datetime import datetime

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

# Ensure backend/ is on the path so relative imports resolve
sys.path.insert(0, os.path.dirname(__file__))

from config import SUPPORTED_LANGUAGES
from audio.capture import AudioCapture
from transcriber.whisper_stt import WhisperTranscriber
from translator.translate import Translator
from speaker_profile.profiler import ProfileManager
from session.manager import SessionManager

app = FastAPI(title="Meeting Translator", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

audio_capture: AudioCapture = None
whisper: WhisperTranscriber = None
translator = Translator()
profile_manager = ProfileManager()
session_manager = SessionManager()


@app.on_event("startup")
async def startup():
    global audio_capture, whisper
    audio_capture = AudioCapture()
    audio_capture.start()   # abre o stream de áudio — sem isso a fila fica vazia para sempre
    whisper = WhisperTranscriber()
    print("✓ Backend initialized")


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/api/system/check")
async def system_check():
    """Return OS info and whether a virtual audio device is present."""
    import platform
    import sounddevice as sd

    os_name = platform.system()  # "Darwin" | "Windows" | "Linux"

    virtual_device = None
    virtual_keywords = {
        "Darwin":  ["blackhole", "black hole"],
        "Windows": ["vb-audio", "virtual cable", "cable output", "cable input", "voicemeeter"],
        "Linux":   ["pulse", "pipewire", "virtual"],
    }
    keywords = virtual_keywords.get(os_name, [])

    try:
        devices = sd.query_devices()
        for d in devices:
            name_lower = d["name"].lower()
            if any(kw in name_lower for kw in keywords):
                virtual_device = d["name"]
                break
    except Exception:
        pass

    download_urls = {
        "Darwin":  {
            "name": "BlackHole",
            "url":  "https://existential.audio/blackhole/",
        },
        "Windows": {
            "name": "VB-Audio Virtual Cable",
            "url":  "https://vb-audio.com/Cable/",
        },
    }

    driver_info = download_urls.get(os_name, {"name": "Virtual Audio Driver", "url": ""})

    return {
        "os":                   os_name,
        "virtual_device_found": virtual_device is not None,
        "virtual_device_name":  virtual_device,
        "driver_name":          driver_info["name"],
        "driver_download_url":  driver_info["url"],
    }


@app.get("/api/languages")
async def get_languages():
    return {"languages": SUPPORTED_LANGUAGES}


_YOUTUBE_URL_RE = re.compile(
    r'^https?://(www\.)?(youtube\.com/watch\?.*v=[\w-]+|youtu\.be/[\w-]+)'
)


@app.post("/api/speaker-profiles")
async def create_speaker_profile(request: dict):
    urls = request.get("urls", [])
    speaker_name = request.get("speaker_name", "Profile")

    if not urls:
        raise HTTPException(status_code=400, detail="No URLs provided")

    invalid = [u for u in urls if not _YOUTUBE_URL_RE.match(str(u))]
    if invalid:
        raise HTTPException(
            status_code=422,
            detail=f"Invalid YouTube URL(s): {', '.join(invalid)}",
        )

    try:
        profile = await profile_manager.create_profile(urls, speaker_name)
        return {"status": "success", **profile}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/speaker-profiles")
async def list_speaker_profiles():
    profiles = profile_manager.list_profiles()
    return {"profiles": profiles}


@app.get("/api/session/{session_id}")
async def get_session(session_id: str):
    session = session_manager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return {
        "session_id": session_id,
        "duration_minutes": session.get("duration_minutes", 0),
        "phrases_translated": len(session["phrases"]),
        "target_language": session["target_lang"],
        "recent_phrases": session["phrases"][-5:],
        "profile_used": session.get("profile_id"),
    }


@app.websocket("/ws/transcribe/{session_id}")
async def websocket_transcribe(websocket: WebSocket, session_id: str):
    await websocket.accept()

    try:
        init_msg = await websocket.receive_json()
        target_lang = init_msg.get("target_lang", "pt")
        profile_id = init_msg.get("profile_id")
    except WebSocketDisconnect:
        # Client disconnected before sending init (e.g. React StrictMode double-mount)
        return
    except Exception:
        return

    session = session_manager.create_session(
        session_id=session_id,
        target_lang=target_lang,
        profile_id=profile_id,
    )

    initial_prompt = None
    if profile_id:
        sp = profile_manager.load_profile(profile_id)
        if sp:
            initial_prompt = sp.initial_prompt
            await websocket.send_json(
                {
                    "type": "status",
                    "message": f"✓ Perfil '{sp.name}' ativo",
                    "icon": "👤",
                }
            )

    loop = asyncio.get_event_loop()

    try:
        while True:
            # get_chunk() is blocking — run in executor to avoid blocking event loop
            chunk = await loop.run_in_executor(None, audio_capture.get_chunk)

            text, detected_lang = await loop.run_in_executor(
                None, whisper.transcribe, chunk, initial_prompt
            )

            if not text or not text.strip():
                continue

            translated = text
            if detected_lang not in ("silent", "error") and detected_lang != target_lang:
                translated = await loop.run_in_executor(
                    None, translator.translate, text, detected_lang, target_lang
                )

            payload = {
                "type": "caption",
                "original": text,
                "translated": translated,
                "language": target_lang,
                "timestamp": datetime.now().isoformat(),
            }
            await websocket.send_json(payload)
            session_manager.add_phrase(session_id, text, translated)

    except WebSocketDisconnect:
        pass
    except Exception as e:
        try:
            await websocket.send_json({"type": "error", "message": str(e)})
        except Exception:
            pass
    finally:
        session_manager.end_session(session_id)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
