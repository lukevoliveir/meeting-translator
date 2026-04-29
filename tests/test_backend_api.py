import pytest
import requests
from conftest import BACKEND_URL


class TestHealthEndpoint:
    """GET /health"""

    def test_health_returns_200(self, backend_service):
        response = requests.get(f"{BACKEND_URL}/health", timeout=5)
        assert response.status_code == 200

    def test_health_status_ok(self, backend_service):
        response = requests.get(f"{BACKEND_URL}/health", timeout=5)
        assert response.json()["status"] == "ok"


class TestLanguageEndpoint:
    """GET /api/languages"""

    def test_languages_returns_200(self, backend_service):
        response = requests.get(f"{BACKEND_URL}/api/languages", timeout=5)
        assert response.status_code == 200

    def test_languages_has_list(self, backend_service):
        response = requests.get(f"{BACKEND_URL}/api/languages", timeout=5)
        data = response.json()
        assert "languages" in data
        assert isinstance(data["languages"], list)

    def test_languages_has_at_least_3(self, backend_service):
        response = requests.get(f"{BACKEND_URL}/api/languages", timeout=5)
        data = response.json()
        assert len(data["languages"]) >= 3

    def test_language_item_structure(self, backend_service):
        response = requests.get(f"{BACKEND_URL}/api/languages", timeout=5)
        lang = response.json()["languages"][0]
        assert "code" in lang
        assert "flag" in lang
        assert "name" in lang

    def test_portuguese_supported(self, backend_service):
        response = requests.get(f"{BACKEND_URL}/api/languages", timeout=5)
        codes = [lang["code"] for lang in response.json()["languages"]]
        assert "pt" in codes, f"Portuguese not found in supported languages: {codes}"

    def test_english_supported(self, backend_service):
        response = requests.get(f"{BACKEND_URL}/api/languages", timeout=5)
        codes = [lang["code"] for lang in response.json()["languages"]]
        assert "en" in codes


class TestSpeakerProfileEndpoint:
    """GET /api/speaker-profiles"""

    def test_list_profiles_returns_200(self, backend_service):
        response = requests.get(f"{BACKEND_URL}/api/speaker-profiles", timeout=5)
        assert response.status_code == 200

    def test_list_profiles_has_profiles_key(self, backend_service):
        response = requests.get(f"{BACKEND_URL}/api/speaker-profiles", timeout=5)
        data = response.json()
        assert "profiles" in data
        assert isinstance(data["profiles"], list)

    def test_post_profile_missing_body_returns_error(self, backend_service):
        response = requests.post(
            f"{BACKEND_URL}/api/speaker-profiles",
            json={},
            timeout=5,
        )
        # Missing required fields should return 4xx
        assert response.status_code in (400, 422)

    def test_post_profile_invalid_url_returns_error(self, backend_service):
        response = requests.post(
            f"{BACKEND_URL}/api/speaker-profiles",
            json={"speaker_name": "Test", "urls": ["not-a-url"]},
            timeout=5,
        )
        assert response.status_code in (400, 422, 500)


class TestSessionEndpoint:
    """GET /api/session/{session_id}"""

    def test_unknown_session_returns_404(self, backend_service):
        response = requests.get(
            f"{BACKEND_URL}/api/session/nonexistent-session-id", timeout=5
        )
        assert response.status_code == 404

    def test_session_id_format_accepted(self, backend_service):
        # Any string is a valid format — 404 means the server understood the request
        response = requests.get(
            f"{BACKEND_URL}/api/session/session-1234567890", timeout=5
        )
        assert response.status_code in (200, 404)
