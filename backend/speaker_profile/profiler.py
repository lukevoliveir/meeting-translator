"""Speaker profile builder - extracts vocabulary and creates Whisper context from audio."""

import json
import os
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import List, Dict, Optional
from collections import Counter
import re


# Common English/Portuguese stopwords to filter
STOPWORDS = {
    # English
    'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
    'of', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has',
    'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may',
    'might', 'can', 'get', 'got', 'make', 'made', 'take', 'took', 'go', 'went',
    'come', 'came', 'see', 'saw', 'know', 'knew', 'think', 'thought', 'say',
    'said', 'tell', 'told', 'want', 'wanted', 'need', 'needed', 'feel', 'felt',
    'try', 'tried', 'ask', 'asked', 'give', 'gave', 'find', 'found', 'work',
    'worked', 'call', 'called', 'use', 'used', 'show', 'showed', 'hear',
    'heard', 'let', 'mean', 'meant', 'keep', 'kept', 'start', 'started',
    'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we',
    'they', 'what', 'which', 'who', 'when', 'where', 'why', 'how',
    # Portuguese
    'o', 'a', 'os', 'as', 'um', 'uma', 'uns', 'umas', 'de', 'da', 'do',
    'das', 'dos', 'e', 'ou', 'mas', 'em', 'no', 'na', 'nos', 'nas', 'por',
    'para', 'com', 'sem', 'sob', 'sobre', 'ante', 'entre', 'até', 'desde',
    'é', 'são', 'era', 'eram', 'ser', 'estou', 'está', 'estamos', 'estão',
    'estive', 'esteve', 'tive', 'teve', 'tenho', 'tem', 'temos', 'têm',
    'tinha', 'tinham', 'faço', 'faz', 'fazemos', 'fazem', 'fiz', 'fizeste',
    'fez', 'fizemos', 'fizeram', 'vou', 'vai', 'vamos', 'vão', 'ia', 'iam',
    'este', 'esse', 'aquele', 'esta', 'essa', 'aquela', 'isto', 'isso',
    'aquilo', 'eu', 'tu', 'ele', 'ela', 'nós', 'vós', 'eles', 'elas',
    'meu', 'teu', 'seu', 'nosso', 'vosso', 'minha', 'tua', 'sua', 'nossa',
    'vossa', 'quem', 'qual', 'quanto', 'onde', 'quando', 'como', 'porque'
}


@dataclass
class SpeakerProfile:
    initial_prompt: str
    glossary: Dict[str, str]
    vocab_list: List[str]
    accent: str
    audio_duration_minutes: float
    name: str = ""

    def to_dict(self) -> Dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict) -> "SpeakerProfile":
        return cls(**data)


def _extract_words(text: str) -> List[str]:
    text = text.lower()
    words = re.findall(r'\b[a-záéíóúàâêôãõçñ]+\b', text)
    return [w for w in words if w and w not in STOPWORDS and len(w) > 2]


def _build_initial_prompt(word_freq: Counter) -> str:
    top_words = [word for word, _ in word_freq.most_common(30)]
    return ", ".join(top_words)


def _build_glossary(word_freq: Counter) -> Dict[str, str]:
    return {
        word: word
        for word, count in word_freq.most_common(50)
        if count >= 2
    }


def build_profile(audio_files: List[str], profile_name: str, whisper_model=None) -> "SpeakerProfile":
    """Build speaker profile from audio files.

    Args:
        audio_files: paths to downloaded MP3 files
        profile_name: display name for the profile
        whisper_model: pre-loaded Whisper model (avoids reloading per call)
    """
    import whisper as _whisper

    model = whisper_model if whisper_model is not None else _whisper.load_model("base")

    try:
        all_words: List[str] = []
        detected_languages: List[str] = []
        total_duration = 0.0

        for audio_file in audio_files:
            if not os.path.exists(audio_file):
                raise ValueError(f"Audio file not found: {audio_file}")

            try:
                import librosa
                audio_array, _ = librosa.load(audio_file, sr=16000)
                total_duration += len(audio_array) / 16000 / 60
            except Exception:
                pass

            try:
                result = model.transcribe(audio_file)
                text = result.get("text", "")
                detected_languages.append(result.get("language", "unknown"))
                all_words.extend(_extract_words(text))
            except Exception as e:
                raise ValueError(f"Failed to transcribe {audio_file}: {e}")

        word_freq = Counter(all_words)
        accent = detected_languages[0] if detected_languages else "unknown"

        profile = SpeakerProfile(
            initial_prompt=_build_initial_prompt(word_freq),
            glossary=_build_glossary(word_freq),
            vocab_list=[w for w, _ in word_freq.most_common(50)],
            accent=accent,
            audio_duration_minutes=total_duration,
            name=profile_name,
        )

        save_profile(profile)
        return profile

    except Exception as e:
        raise ValueError(f"Failed to build profile: {e}")


def save_profile(profile: SpeakerProfile) -> str:
    from .downloader import get_profiles_dir

    profiles_dir = get_profiles_dir()
    profile_path = profiles_dir / f"{profile.name}.json"

    # Avoid silently overwriting an existing profile
    if profile_path.exists():
        raise ValueError(
            f"A profile named '{profile.name}' already exists. "
            "Choose a different name or delete the existing one first."
        )

    try:
        with open(profile_path, "w", encoding="utf-8") as f:
            json.dump(profile.to_dict(), f, indent=2, ensure_ascii=False)
        return str(profile_path)
    except Exception as e:
        raise ValueError(f"Failed to save profile: {e}")


def load_profile(profile_name: str) -> Optional[SpeakerProfile]:
    from .downloader import get_profiles_dir

    profiles_dir = get_profiles_dir()
    profile_path = profiles_dir / f"{profile_name}.json"

    if not profile_path.exists():
        return None

    try:
        with open(profile_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return SpeakerProfile.from_dict(data)
    except Exception as e:
        raise ValueError(f"Failed to load profile: {e}")


def list_profiles() -> List[str]:
    from .downloader import get_profiles_dir

    try:
        profiles_dir = get_profiles_dir()
        return sorted(f.stem for f in profiles_dir.glob("*.json"))
    except Exception:
        return []


def delete_profile(profile_name: str) -> None:
    from .downloader import get_profiles_dir

    profiles_dir = get_profiles_dir()
    profile_path = profiles_dir / f"{profile_name}.json"

    try:
        if profile_path.exists():
            profile_path.unlink()
    except Exception as e:
        raise ValueError(f"Failed to delete profile: {e}")


class ProfileManager:
    def __init__(self):
        self._whisper_model = None

    def _get_whisper_model(self):
        """Lazy-load the Whisper model once and reuse it."""
        if self._whisper_model is None:
            import whisper as _whisper
            self._whisper_model = _whisper.load_model("base")
        return self._whisper_model

    def _sync_create_profile(self, urls: list, speaker_name: str) -> dict:
        """Blocking work: download audio, transcribe, build profile. Run via executor."""
        from speaker_profile.downloader import download_audio, cleanup_temp_audio

        audio_files: list = []
        try:
            for i, url in enumerate(urls):
                path = download_audio(url, f"tmp_{speaker_name}_{i}")
                audio_files.append(path)

            model = self._get_whisper_model()
            profile = build_profile(audio_files, speaker_name, whisper_model=model)
        finally:
            # Always clean up temp files, even if transcription failed
            for f in audio_files:
                cleanup_temp_audio(f)

        return {
            "id": profile.name,
            "speaker_name": profile.name,
            "vocabulary": profile.vocab_list,
            "initial_prompt": profile.initial_prompt,
            "stats": {
                "unique_words": len(profile.vocab_list),
                "accent": profile.accent,
                "duration_minutes": profile.audio_duration_minutes,
            },
        }

    async def create_profile(self, urls: list, speaker_name: str) -> dict:
        """Run blocking download+transcription in a thread so the event loop stays free."""
        import asyncio
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None, self._sync_create_profile, urls, speaker_name
        )

    def list_profiles(self) -> list:
        return list_profiles()

    def load_profile(self, profile_id: str):
        return load_profile(profile_id)
