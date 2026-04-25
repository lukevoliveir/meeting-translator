"""System audio capture module using sounddevice with loopback audio."""

import platform
import threading
from queue import Queue
from typing import Optional

import numpy as np
import sounddevice as sd

from config import CHUNK_SECONDS, SAMPLE_RATE


class AudioCapture:
    """Captures system audio via loopback device in a background thread."""

    def __init__(self):
        """Initialize audio capture with platform-specific loopback device detection."""
        self.sample_rate = SAMPLE_RATE
        self.chunk_size = SAMPLE_RATE * CHUNK_SECONDS
        self.chunk_queue: Queue = Queue()
        self.is_recording = False
        self.stream: Optional[sd.InputStream] = None
        self._device_id = self._detect_loopback_device()
        self._thread: Optional[threading.Thread] = None

    def _detect_loopback_device(self) -> int:
        """
        Detect the loopback audio device based on the platform.

        Returns:
            Device ID for the loopback device.

        Raises:
            RuntimeError: If no loopback device is found.
        """
        system = platform.system()

        if system == "Windows":
            return self._find_windows_loopback()
        elif system == "Darwin":
            return self._find_macos_loopback()
        elif system == "Linux":
            return self._find_linux_loopback()
        else:
            raise RuntimeError(f"Unsupported operating system: {system}")

    def _find_windows_loopback(self) -> int:
        """
        Find Windows WASAPI loopback device (Stereo Mix).

        Returns:
            Device ID for WASAPI loopback.

        Raises:
            RuntimeError: If Stereo Mix is not found.
        """
        devices = sd.query_devices()
        for i, device in enumerate(devices):
            name = device["name"].lower()
            if "loopback" in name or "stereo mix" in name:
                if device["max_input_channels"] > 0:
                    return i

        raise RuntimeError(
            "Stereo Mix not found on this Windows system.\n"
            "To enable Stereo Mix:\n"
            "1. Open Control Panel > Sound\n"
            "2. Go to the Recording tab\n"
            "3. Right-click in empty space > Show Disabled Devices\n"
            "4. Right-click 'Stereo Mix' > Enable\n"
            "5. Set as default device\n"
            "6. Click Apply and OK"
        )

    def _find_macos_loopback(self) -> int:
        """
        Find macOS BlackHole virtual audio device.

        Returns:
            Device ID for BlackHole.

        Raises:
            RuntimeError: If BlackHole is not found.
        """
        devices = sd.query_devices()
        for i, device in enumerate(devices):
            if "blackhole" in device["name"].lower():
                if device["max_input_channels"] > 0:
                    return i

        raise RuntimeError(
            "BlackHole virtual audio device not found.\n"
            "To enable audio capture on macOS:\n"
            "1. Install BlackHole from: https://existential.audio/blackhole/\n"
            "2. Restart your Mac\n"
            "3. Go to System Preferences > Sound > Output\n"
            "4. Select BlackHole as output device\n"
            "5. Run this application again"
        )

    def _find_linux_loopback(self) -> int:
        """
        Find Linux PulseAudio monitor device.

        Returns:
            Device ID for PulseAudio monitor.

        Raises:
            RuntimeError: If no monitor device is found.
        """
        devices = sd.query_devices()
        for i, device in enumerate(devices):
            name = device["name"].lower()
            if "monitor" in name and device["max_input_channels"] > 0:
                return i

        raise RuntimeError(
            "PulseAudio monitor device not found.\n"
            "Ensure PulseAudio is properly configured with loopback:\n"
            "1. Install pactl: sudo apt-get install pulseaudio-utils\n"
            "2. Load loopback module: pactl load-module module-loopback\n"
            "3. Run this application again"
        )

    def _audio_callback(self, indata: np.ndarray, frames: int, time_info, status):
        """
        Callback for audio stream. Puts audio chunks into the queue.

        Args:
            indata: Audio data from the stream.
            frames: Number of frames in this callback.
            time_info: Time information.
            status: Status flags.
        """
        if status:
            print(f"Audio stream warning: {status}")

        # Ensure we have exactly chunk_size samples
        if indata.shape[0] == self.chunk_size:
            audio_chunk = indata[:, 0].copy() if indata.ndim > 1 else indata.copy()
            self.chunk_queue.put(audio_chunk.astype(np.float32))

    def start(self) -> None:
        """Start capturing audio from the loopback device."""
        if self.is_recording:
            return

        self.is_recording = True

        try:
            self.stream = sd.InputStream(
                device=self._device_id,
                samplerate=self.sample_rate,
                channels=1,
                blocksize=self.chunk_size,
                callback=self._audio_callback,
                latency="low",
            )
            self.stream.start()
            print(f"Audio capture started on device {self._device_id}")
        except Exception as e:
            self.is_recording = False
            raise RuntimeError(f"Failed to start audio capture: {e}")

    def stop(self) -> None:
        """Stop capturing audio."""
        self.is_recording = False
        if self.stream:
            self.stream.stop()
            self.stream.close()
            self.stream = None
        print("Audio capture stopped")

    def get_chunk(self) -> np.ndarray:
        """
        Get the next audio chunk from the queue. Blocks until available.

        Returns:
            Audio chunk as numpy float32 array with shape (SAMPLE_RATE * CHUNK_SECONDS,).
        """
        return self.chunk_queue.get()

    def get_device_info(self) -> dict:
        """
        Get information about the current loopback device.

        Returns:
            Dictionary with device information.
        """
        return sd.query_devices(self._device_id)
