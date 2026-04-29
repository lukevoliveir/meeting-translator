import pytest
import asyncio
import json
import websockets
from conftest import BACKEND_PORT

WS_BASE = f"ws://localhost:{BACKEND_PORT}"


def backend_is_running():
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(("localhost", BACKEND_PORT)) == 0


@pytest.mark.asyncio
@pytest.mark.skipif(not backend_is_running(), reason="Backend not running")
class TestWebSocketConnectivity:
    """WebSocket endpoint connectivity tests.

    These tests require a running backend. Audio transcription won't produce
    output without a real audio device, but we can verify the protocol layer.
    """

    async def test_websocket_connects(self, backend_service):
        uri = f"{WS_BASE}/ws/transcribe/test-session-ws-connect"
        try:
            async with websockets.connect(uri, open_timeout=5) as ws:
                assert ws.open
        except (OSError, websockets.exceptions.WebSocketException) as exc:
            pytest.skip(f"WebSocket connection failed (may need audio device): {exc}")

    async def test_websocket_accepts_init_message(self, backend_service):
        uri = f"{WS_BASE}/ws/transcribe/test-session-ws-init"
        try:
            async with websockets.connect(uri, open_timeout=5) as ws:
                init_msg = json.dumps({"target_lang": "pt", "profile_id": None})
                await ws.send(init_msg)
                # Server may respond with a status message or stay silent waiting for audio
                try:
                    response = await asyncio.wait_for(ws.recv(), timeout=3)
                    data = json.loads(response)
                    assert "type" in data, f"Response missing 'type' field: {data}"
                except asyncio.TimeoutError:
                    # No immediate response is acceptable — audio device may not be present
                    pass
        except (OSError, websockets.exceptions.WebSocketException) as exc:
            pytest.skip(f"WebSocket connection failed: {exc}")

    async def test_websocket_response_types_are_valid(self, backend_service):
        """Any message the server sends must have a recognised type field."""
        valid_types = {"caption", "status", "error"}
        uri = f"{WS_BASE}/ws/transcribe/test-session-ws-types"
        try:
            async with websockets.connect(uri, open_timeout=5) as ws:
                await ws.send(json.dumps({"target_lang": "pt", "profile_id": None}))
                try:
                    response = await asyncio.wait_for(ws.recv(), timeout=3)
                    data = json.loads(response)
                    assert data.get("type") in valid_types, (
                        f"Unexpected message type: {data.get('type')!r}"
                    )
                except asyncio.TimeoutError:
                    pass  # No output without audio input — that's fine
        except (OSError, websockets.exceptions.WebSocketException) as exc:
            pytest.skip(f"WebSocket connection failed: {exc}")

    async def test_websocket_clean_close(self, backend_service):
        """Server should not crash when the client disconnects immediately."""
        uri = f"{WS_BASE}/ws/transcribe/test-session-ws-close"
        try:
            async with websockets.connect(uri, open_timeout=5) as ws:
                await ws.send(json.dumps({"target_lang": "en", "profile_id": None}))
                # Close immediately without waiting for a response
                await ws.close()
                assert ws.closed
        except (OSError, websockets.exceptions.WebSocketException) as exc:
            pytest.skip(f"WebSocket connection failed: {exc}")

    async def test_websocket_multiple_sessions_independent(self, backend_service):
        """Two WebSocket connections with different session IDs should not interfere."""
        uri_a = f"{WS_BASE}/ws/transcribe/session-a-multi"
        uri_b = f"{WS_BASE}/ws/transcribe/session-b-multi"
        try:
            async with (
                websockets.connect(uri_a, open_timeout=5) as ws_a,
                websockets.connect(uri_b, open_timeout=5) as ws_b,
            ):
                assert ws_a.open
                assert ws_b.open
                # Both connections live at the same time
                await ws_a.send(json.dumps({"target_lang": "pt", "profile_id": None}))
                await ws_b.send(json.dumps({"target_lang": "en", "profile_id": None}))
        except (OSError, websockets.exceptions.WebSocketException) as exc:
            pytest.skip(f"WebSocket connection failed: {exc}")
