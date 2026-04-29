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
from audio.capture import AudioCapture, list_all_loopback_candidates
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
audio_capture_error: str = None   # set when AudioCapture init fails at startup
whisper: WhisperTranscriber = None
translator = Translator()
profile_manager = ProfileManager()
session_manager = SessionManager()


@app.on_event("startup")
async def startup():
    global audio_capture, audio_capture_error, whisper
    try:
        audio_capture = AudioCapture()
        audio_capture.start()
    except Exception as exc:
        audio_capture_error = str(exc)
        print(f"[audio] Startup warning — no loopback device: {exc}")
    whisper = WhisperTranscriber()
    print("✓ Backend initialized")


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/api/system/check")
async def system_check():
    """Return OS info and active loopback device status."""
    import platform

    os_name = platform.system()

    driver_download = {
        "Darwin":  {"name": "BlackHole",              "url": "https://existential.audio/blackhole/"},
        "Windows": {"name": "VB-Audio Virtual Cable", "url": "https://vb-audio.com/Cable/"},
    }
    driver_info = driver_download.get(os_name, {"name": "Virtual Audio Driver", "url": ""})

    if audio_capture is not None:
        dev = audio_capture.get_device_info()
        loopback_found = True
        device_name   = dev["name"]
        device_method = dev["method"]
        device_backend = dev["backend"]
    else:
        loopback_found = False
        device_name    = None
        device_method  = None
        device_backend = None

    return {
        "os":                   os_name,
        # new fields
        "loopback_found":       loopback_found,
        "device_name":          device_name,
        "device_method":        device_method,
        "device_backend":       device_backend,
        "capture_error":        audio_capture_error,
        "driver_name":          driver_info["name"],
        "driver_download_url":  driver_info["url"],
        # kept for backward compatibility
        "virtual_device_found": loopback_found,
        "virtual_device_name":  device_name,
    }


@app.get("/audio/devices")
async def get_audio_devices():
    """Diagnostic endpoint — list all loopback candidates and current device."""
    current = audio_capture.get_device_info() if audio_capture else None
    candidates = list_all_loopback_candidates()
    wasapi_available = any(c["backend"] == "pyaudiowpatch" for c in candidates)

    return {
        "current_device":          current,
        "capture_error":           audio_capture_error,
        "candidates":              candidates,
        "wasapi_native_available": wasapi_available,
        "manual_override":         os.environ.get("AUDIO_LOOPBACK_DEVICE", ""),
        "vb_cable_download":       "https://vb-audio.com/Cable/",
        "blackhole_download":      "https://existential.audio/blackhole/",
    }


@app.put("/audio/device")
async def switch_audio_device(body: dict):
    """Switch loopback device at runtime (use device name or 'wasapi_native')."""
    global audio_capture, audio_capture_error

    device_name = (body.get("name") or "").strip()
    if not device_name:
        raise HTTPException(status_code=400, detail="'name' field is required")

    if audio_capture is None:
        # Try to create a fresh capture with the requested device
        try:
            os.environ["AUDIO_LOOPBACK_DEVICE"] = device_name
            audio_capture = AudioCapture()
            audio_capture.start()
            audio_capture_error = None
        except Exception as exc:
            audio_capture_error = str(exc)
            os.environ.pop("AUDIO_LOOPBACK_DEVICE", None)
            raise HTTPException(status_code=500, detail=str(exc))
        finally:
            os.environ.pop("AUDIO_LOOPBACK_DEVICE", None)
    else:
        try:
            audio_capture.switch_device(device_name)
            audio_capture_error = None
        except Exception as exc:
            audio_capture_error = str(exc)
            raise HTTPException(status_code=500, detail=str(exc))

    return {"status": "ok", "device": audio_capture.get_device_info()}


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

    if audio_capture is None:
        await websocket.send_json({
            "type": "error",
            "message": audio_capture_error or "Nenhum dispositivo de loopback encontrado. Instale BlackHole (Mac) ou VB-Audio CABLE (Windows).",
        })
        await websocket.close()
        return

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
    silence_count = 0
    SILENCE_WARNING_AFTER = 3  # chunks × 5s = 15 segundos sem áudio

    try:
        while True:
            # get_chunk() is blocking — run in executor to avoid blocking event loop
            chunk = await loop.run_in_executor(None, audio_capture.get_chunk)

            text, detected_lang = await loop.run_in_executor(
                None, whisper.transcribe, chunk, initial_prompt
            )

            if not text or not text.strip():
                silence_count += 1
                if silence_count == SILENCE_WARNING_AFTER:
                    device_name = audio_capture.get_device_info()["name"]
                    await websocket.send_json({
                        "type": "warning",
                        "message": (
                            f"Capturando de '{device_name}' mas sem áudio detectado. "
                            "Certifique-se que o Google Meet/Zoom está usando este dispositivo "
                            "como saída de áudio."
                        ),
                    })
                continue

            silence_count = 0

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
