"""System audio capture — supports WASAPI native loopback, Stereo Mix,
VB-Audio Virtual Cable, VoiceMeeter, BlackHole, and PulseAudio monitors.

Priority on Windows:
  1. AUDIO_LOOPBACK_DEVICE env var (manual override)
  2. pyaudiowpatch WASAPI native loopback (no driver install required)
  3. Stereo Mix (Realtek / generic)
  4. CABLE Output (VB-Audio Virtual Cable)
  5. VoiceMeeter Output
  6. Any device whose name contains a loopback keyword
"""

import os
import platform
import threading
from dataclasses import dataclass, field
from queue import Queue
from typing import Optional

import numpy as np
import sounddevice as sd

from config import CHUNK_SECONDS, SAMPLE_RATE


# ---------------------------------------------------------------------------
# Priority-ordered keyword → method map (Windows / generic search)
# ---------------------------------------------------------------------------
_WINDOWS_PRIORITY = [
    ("stereo mix",         "stereo_mix"),
    ("cable output",       "vb_cable"),
    ("voicemeeter output", "voicemeeter"),
    ("loopback",           "keyword"),
    ("what u hear",        "keyword"),
    ("wave out mix",       "keyword"),
    ("mix",                "keyword"),
]


@dataclass
class LoopbackDevice:
    """Describes the selected loopback audio source."""
    name: str
    method: str        # wasapi_native | stereo_mix | vb_cable | voicemeeter | keyword
                       # blackhole | pulse_monitor | microphone_fallback | manual
    backend: str       # pyaudiowpatch | sounddevice
    device_id: Optional[int] = None   # sounddevice index; None for pyaudiowpatch
    channels: int = 1
    sample_rate: int = SAMPLE_RATE


# ---------------------------------------------------------------------------
# AudioCapture
# ---------------------------------------------------------------------------

class AudioCapture:
    """Captures system audio via the best available loopback mechanism."""

    def __init__(self):
        self.sample_rate = SAMPLE_RATE
        self.chunk_size = SAMPLE_RATE * CHUNK_SECONDS
        self.chunk_queue: Queue = Queue()
        self.is_recording = False
        self._stream = None     # sd.InputStream or pyaudiowpatch stream
        self._pa = None         # PyAudio instance when using pyaudiowpatch
        self._device: LoopbackDevice = self._detect_loopback_device()
        print(
            f"[audio] Device selected: {self._device.name!r}"
            f"  method={self._device.method}  backend={self._device.backend}"
        )

    # ------------------------------------------------------------------
    # Detection
    # ------------------------------------------------------------------

    def _detect_loopback_device(self) -> LoopbackDevice:
        # 1. Manual override
        forced = os.environ.get("AUDIO_LOOPBACK_DEVICE", "").strip()
        if forced:
            return self._find_device_by_name(forced)

        system = platform.system()
        if system == "Windows":
            return self._find_windows_loopback()
        elif system == "Darwin":
            return self._find_macos_loopback()
        elif system == "Linux":
            return self._find_linux_loopback()
        else:
            raise RuntimeError(f"Unsupported operating system: {system}")

    def _find_device_by_name(self, target: str) -> LoopbackDevice:
        """Find a sounddevice input by name substring (case-insensitive)."""
        target_lower = target.lower()
        for i, d in enumerate(sd.query_devices()):
            if target_lower in d["name"].lower() and d["max_input_channels"] > 0:
                return LoopbackDevice(
                    name=d["name"], method="manual",
                    backend="sounddevice", device_id=i,
                )
        raise RuntimeError(
            f"Device '{target}' (AUDIO_LOOPBACK_DEVICE) not found.\n"
            f"Available input devices:\n{_list_input_devices()}"
        )

    def _find_windows_loopback(self) -> LoopbackDevice:
        # 1. pyaudiowpatch WASAPI native loopback (preferred)
        dev = _try_wasapi_loopback()
        if dev:
            return dev

        # 2. Named loopback devices via sounddevice
        devices = sd.query_devices()
        for pattern, method in _WINDOWS_PRIORITY:
            for i, d in enumerate(devices):
                if pattern in d["name"].lower() and d["max_input_channels"] > 0:
                    return LoopbackDevice(
                        name=d["name"], method=method,
                        backend="sounddevice", device_id=i,
                    )

        raise RuntimeError(_windows_error_message())

    def _find_macos_loopback(self) -> LoopbackDevice:
        devices = sd.query_devices()
        for i, d in enumerate(devices):
            if "blackhole" in d["name"].lower() and d["max_input_channels"] > 0:
                return LoopbackDevice(
                    name=d["name"], method="blackhole",
                    backend="sounddevice", device_id=i,
                )

        print(
            "[audio] BlackHole not found — falling back to built-in microphone.\n"
            "        Install BlackHole for system audio: https://existential.audio/blackhole/"
        )
        for i, d in enumerate(devices):
            if any(k in d["name"].lower() for k in ("macbook", "built-in", "microfone")) \
                    and d["max_input_channels"] > 0:
                return LoopbackDevice(
                    name=d["name"], method="microphone_fallback",
                    backend="sounddevice", device_id=i,
                )
        for i, d in enumerate(devices):
            if d["max_input_channels"] > 0:
                return LoopbackDevice(
                    name=d["name"], method="microphone_fallback",
                    backend="sounddevice", device_id=i,
                )
        raise RuntimeError("No audio input device found on macOS.")

    def _find_linux_loopback(self) -> LoopbackDevice:
        for i, d in enumerate(sd.query_devices()):
            if "monitor" in d["name"].lower() and d["max_input_channels"] > 0:
                return LoopbackDevice(
                    name=d["name"], method="pulse_monitor",
                    backend="sounddevice", device_id=i,
                )
        raise RuntimeError(
            "PulseAudio monitor device not found.\n"
            "Run: pactl load-module module-loopback\n"
            "Then restart the application."
        )

    # ------------------------------------------------------------------
    # Stream lifecycle
    # ------------------------------------------------------------------

    def start(self) -> None:
        if self.is_recording:
            return
        self.is_recording = True
        try:
            if self._device.backend == "pyaudiowpatch":
                self._start_wasapi_loopback()
            else:
                self._start_sounddevice()
            print(f"[audio] Capture started — {self._device.name!r}")
        except Exception as exc:
            self.is_recording = False
            raise RuntimeError(f"Failed to start audio capture: {exc}") from exc

    def _start_wasapi_loopback(self) -> None:
        import pyaudiowpatch as pyaudio  # type: ignore

        channels = self._device.channels
        native_rate = self._device.sample_rate
        native_chunk = int(native_rate * CHUNK_SECONDS)

        def _pa_callback(in_data, frame_count, time_info, status):
            if in_data:
                audio = np.frombuffer(in_data, dtype=np.float32).copy()
                if channels > 1:
                    audio = audio.reshape(-1, channels).mean(axis=1)
                if native_rate != SAMPLE_RATE:
                    import librosa  # type: ignore
                    audio = librosa.resample(audio, orig_sr=native_rate, target_sr=SAMPLE_RATE)
                expected = SAMPLE_RATE * CHUNK_SECONDS
                if len(audio) < expected:
                    audio = np.pad(audio, (0, expected - len(audio)))
                else:
                    audio = audio[:expected]
                self.chunk_queue.put(audio.astype(np.float32))
            return (None, pyaudio.paContinue)

        self._pa = pyaudio.PyAudio()
        self._stream = self._pa.open(
            format=pyaudio.paFloat32,
            channels=channels,
            rate=native_rate,
            input=True,
            input_device_index=self._device.device_id,
            as_loopback=True,
            frames_per_buffer=native_chunk,
            stream_callback=_pa_callback,
        )
        self._stream.start_stream()

    def _start_sounddevice(self) -> None:
        def _sd_callback(indata: np.ndarray, frames: int, time_info, status):
            if status:
                print(f"[audio] Stream warning: {status}")
            if indata.shape[0] == self.chunk_size:
                audio = indata[:, 0].copy() if indata.ndim > 1 else indata.copy()
                self.chunk_queue.put(audio.astype(np.float32))

        self._stream = sd.InputStream(
            device=self._device.device_id,
            samplerate=self.sample_rate,
            channels=1,
            blocksize=self.chunk_size,
            callback=_sd_callback,
            latency="low",
        )
        self._stream.start()

    def stop(self) -> None:
        self.is_recording = False
        if self._stream:
            if self._device.backend == "pyaudiowpatch":
                self._stream.stop_stream()
                self._stream.close()
            else:
                self._stream.stop()
                self._stream.close()
            self._stream = None
        if self._pa:
            self._pa.terminate()
            self._pa = None
        print("[audio] Capture stopped.")

    def switch_device(self, device_name: str) -> None:
        """Stop current stream, switch to a different device, and restart."""
        was_recording = self.is_recording
        if was_recording:
            self.stop()

        # Clear any buffered chunks so stale audio is not transcribed
        while not self.chunk_queue.empty():
            self.chunk_queue.get_nowait()

        forced = device_name.strip()
        if forced.lower() == "wasapi_native":
            dev = _try_wasapi_loopback()
            if dev is None:
                raise RuntimeError("WASAPI native loopback is not available on this system.")
            self._device = dev
        else:
            self._device = self._find_device_by_name(forced)

        print(
            f"[audio] Switched to: {self._device.name!r}"
            f"  method={self._device.method}  backend={self._device.backend}"
        )

        if was_recording:
            self.start()

    def get_chunk(self) -> np.ndarray:
        """Block until the next audio chunk is available, then return it."""
        return self.chunk_queue.get()

    # ------------------------------------------------------------------
    # Diagnostics
    # ------------------------------------------------------------------

    def get_device_info(self) -> dict:
        return {
            "name": self._device.name,
            "method": self._device.method,
            "backend": self._device.backend,
            "device_id": self._device.device_id,
            "is_recording": self.is_recording,
        }


# ---------------------------------------------------------------------------
# Module-level helpers (used by diagnostics endpoint without an instance)
# ---------------------------------------------------------------------------

def _try_wasapi_loopback() -> Optional[LoopbackDevice]:
    """Return a LoopbackDevice for WASAPI native loopback, or None if unavailable."""
    try:
        import pyaudiowpatch as pyaudio  # type: ignore
        pa = pyaudio.PyAudio()
        try:
            wasapi_info = pa.get_host_api_info_by_type(pyaudio.paWASAPI)
            default_out = wasapi_info["defaultOutputDevice"]
            if default_out < 0:
                return None
            info = pa.get_device_info_by_index(default_out)
            return LoopbackDevice(
                name=f"{info.get('name', 'Default Output')} (WASAPI Loopback)",
                method="wasapi_native",
                backend="pyaudiowpatch",
                device_id=default_out,
                channels=min(info.get("maxOutputChannels", 2), 2),
                sample_rate=int(info.get("defaultSampleRate", SAMPLE_RATE)),
            )
        finally:
            pa.terminate()
    except Exception:
        return None


def list_all_loopback_candidates() -> list:
    """Return every device that could serve as a loopback source."""
    candidates: list = []

    # WASAPI native via pyaudiowpatch
    wasapi = _try_wasapi_loopback()
    if wasapi:
        candidates.append({
            "name": wasapi.name,
            "method": wasapi.method,
            "backend": wasapi.backend,
            "device_id": wasapi.device_id,
            "recommended": True,
            "note": "Nenhum driver adicional necessário",
        })

    # sounddevice named devices
    keywords_map = [
        ("stereo mix",         "stereo_mix"),
        ("cable output",       "vb_cable"),
        ("voicemeeter output", "voicemeeter"),
        ("blackhole",          "blackhole"),
        ("loopback",           "keyword"),
        ("what u hear",        "keyword"),
        ("wave out mix",       "keyword"),
        ("mix",                "keyword"),
        ("monitor",            "pulse_monitor"),
    ]
    seen_ids: set = set()
    try:
        for i, d in enumerate(sd.query_devices()):
            if d["max_input_channels"] <= 0 or i in seen_ids:
                continue
            name_lower = d["name"].lower()
            for kw, method in keywords_map:
                if kw in name_lower:
                    seen_ids.add(i)
                    candidates.append({
                        "name": d["name"],
                        "method": method,
                        "backend": "sounddevice",
                        "device_id": i,
                        "recommended": False,
                        "note": "",
                    })
                    break
    except Exception:
        pass

    return candidates


def _list_input_devices() -> str:
    try:
        lines = [
            f"  [{i}] {d['name']} ({d['max_input_channels']} ch)"
            for i, d in enumerate(sd.query_devices())
            if d["max_input_channels"] > 0
        ]
        return "\n".join(lines) or "  (none found)"
    except Exception:
        return "  (unable to query devices)"


def _windows_error_message() -> str:
    return (
        "No loopback audio device found.\n\n"
        f"Available recording devices:\n{_list_input_devices()}\n\n"
        "How to fix:\n"
        "  1. WASAPI Native Loopback (recommended — no install needed):\n"
        "       pip install pyaudiowpatch\n\n"
        "  2. VB-Audio Virtual Cable (free virtual driver):\n"
        "       https://vb-audio.com/Cable/\n"
        "       After installing, set 'CABLE Output' as default recording device.\n\n"
        "  3. Stereo Mix (if your sound card supports it):\n"
        "       Control Panel > Sound > Recording > right-click > Show Disabled Devices\n"
        "       Enable 'Stereo Mix'\n\n"
        "  4. Force a specific device:\n"
        "       set AUDIO_LOOPBACK_DEVICE=CABLE Output"
    )
