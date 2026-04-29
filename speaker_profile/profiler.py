"""Speaker profile builder - extracts vocabulary and creates Whisper context from audio."""

import json
import os
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import List, Dict, Optional
from collections import Counter
import re

import numpy as np


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
    """Profile containing speaker-specific vocabulary and transcription context."""
    initial_prompt: str
    glossary: Dict[str, str]
    vocab_list: List[str]
    accent: str
    audio_duration_minutes: float
    name: str = ""

    def to_dict(self) -> Dict:
        """Convert profile to dictionary for JSON serialization."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict) -> "SpeakerProfile":
        """Create profile from dictionary."""
        return cls(**data)


def _extract_words(text: str) -> List[str]:
    """
    Extract words from text, filtering special characters.

    Args:
        text: Input text

    Returns:
        List of cleaned words
    """
    # Convert to lowercase and remove special characters
    text = text.lower()
    # Keep only alphanumeric and basic punctuation
    words = re.findall(r'\b[a-záéíóúàâêôãõçñ]+\b', text)
    return [w for w in words if w and w not in STOPWORDS and len(w) > 2]


def _build_initial_prompt(word_freq: Counter) -> str:
    """
    Build initial_prompt for Whisper from top technical terms.

    Args:
        word_freq: Word frequency counter

    Returns:
        Initial prompt string (top 30 terms)
    """
    top_words = [word for word, _ in word_freq.most_common(30)]
    return ", ".join(top_words)


def _build_glossary(word_freq: Counter) -> Dict[str, str]:
    """
    Build glossary from top technical/domain-specific terms.

    Args:
        word_freq: Word frequency counter

    Returns:
        Dictionary mapping term to term (for preservation)
    """
    # Terms that appear frequently are likely domain-specific
    glossary = {}
    for word, count in word_freq.most_common(50):
        if count >= 2:  # Must appear at least twice
            glossary[word] = word
    return glossary


def build_profile(
    audio_files: List[str],
    profile_name: str
) -> SpeakerProfile:
    """
    Build speaker profile from audio files.

    Args:
        audio_files: List of paths to audio files
        profile_name: Name for the profile

    Returns:
        SpeakerProfile object

    Raises:
        ValueError: If audio files cannot be processed
    """
    # Import here to avoid circular dependency
    from transcriber.whisper_stt import load_model, transcribe
    from audio.capture import AudioCapture

    try:
        # Load Whisper model
        model = load_model("base")

        # Process each audio file
        all_words = []
        detected_languages = []
        total_duration = 0

        for audio_file in audio_files:
            if not os.path.exists(audio_file):
                raise ValueError(f"Audio file not found: {audio_file}")

            # Get file duration using librosa
            try:
                import librosa
                duration, _ = librosa.load(audio_file, sr=16000)
                duration_minutes = len(duration) / 16000 / 60
                total_duration += duration_minutes
            except Exception:
                duration_minutes = 0

            # Transcribe audio file
            try:
                # Load audio and transcribe in chunks
                audio, sr = librosa.load(audio_file, sr=16000)
                # Convert to the format Whisper expects
                result = model.transcribe(audio_file)
                text = result.get("text", "")
                detected_lang = result.get("language", "unknown")

                detected_languages.append(detected_lang)

                # Extract words
                words = _extract_words(text)
                all_words.extend(words)

            except Exception as e:
                raise ValueError(f"Failed to transcribe {audio_file}: {e}")

        # Build frequency counter
        word_freq = Counter(all_words)

        # Detect accent from most common language
        accent = detected_languages[0] if detected_languages else "unknown"

        # Build initial_prompt and glossary
        initial_prompt = _build_initial_prompt(word_freq)
        glossary = _build_glossary(word_freq)
        vocab_list = [word for word, _ in word_freq.most_common(50)]

        # Create profile
        profile = SpeakerProfile(
            initial_prompt=initial_prompt,
            glossary=glossary,
            vocab_list=vocab_list,
            accent=accent,
            audio_duration_minutes=total_duration,
            name=profile_name
        )

        # Save to disk
        save_profile(profile)

        return profile

    except Exception as e:
        raise ValueError(f"Failed to build profile: {e}")


def save_profile(profile: SpeakerProfile) -> str:
    """
    Save speaker profile to disk.

    Args:
        profile: SpeakerProfile object

    Returns:
        Path to saved profile

    Raises:
        ValueError: If save fails
    """
    from .downloader import get_profiles_dir

    try:
        profiles_dir = get_profiles_dir()
        profile_path = profiles_dir / f"{profile.name}.json"

        with open(profile_path, "w", encoding="utf-8") as f:
            json.dump(profile.to_dict(), f, indent=2, ensure_ascii=False)

        return str(profile_path)

    except Exception as e:
        raise ValueError(f"Failed to save profile: {e}")


def load_profile(profile_name: str) -> Optional[SpeakerProfile]:
    """
    Load speaker profile from disk.

    Args:
        profile_name: Name of the profile to load

    Returns:
        SpeakerProfile object or None if not found

    Raises:
        ValueError: If profile cannot be loaded
    """
    from .downloader import get_profiles_dir

    try:
        profiles_dir = get_profiles_dir()
        profile_path = profiles_dir / f"{profile_name}.json"

        if not profile_path.exists():
            return None

        with open(profile_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        return SpeakerProfile.from_dict(data)

    except Exception as e:
        raise ValueError(f"Failed to load profile: {e}")


def list_profiles() -> List[str]:
    """
    List all saved speaker profiles.

    Returns:
        List of profile names
    """
    from .downloader import get_profiles_dir

    try:
        profiles_dir = get_profiles_dir()
        if not profiles_dir.exists():
            return []

        profiles = []
        for file in profiles_dir.glob("*.json"):
            profiles.append(file.stem)

        return sorted(profiles)

    except Exception:
        return []


def delete_profile(profile_name: str) -> None:
    """
    Delete a saved speaker profile.

    Args:
        profile_name: Name of the profile to delete

    Raises:
        ValueError: If deletion fails
    """
    from .downloader import get_profiles_dir

    try:
        profiles_dir = get_profiles_dir()
        profile_path = profiles_dir / f"{profile_name}.json"

        if profile_path.exists():
            profile_path.unlink()

    except Exception as e:
        raise ValueError(f"Failed to delete profile: {e}")
