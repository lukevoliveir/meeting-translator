"""Translation module using Google Translator via deep-translator."""

from deep_translator import GoogleTranslator

from config import TARGET_LANG


# Language code mapping for ISO 639-1 to language names
LANGUAGE_NAMES = {
    "pt": "Portuguese",
    "en": "English",
    "es": "Spanish",
    "fr": "French",
    "de": "German",
    "it": "Italian",
    "ja": "Japanese",
    "ko": "Korean",
    "zh": "Chinese",
    "ru": "Russian",
    "ar": "Arabic",
    "hi": "Hindi",
}


def translate(text: str, source_lang: str, target_lang: str) -> str:
    """
    Translate text from source language to target language.

    Args:
        text: Text to translate.
        source_lang: Source language code (ISO 639-1, e.g., 'en').
        target_lang: Target language code (ISO 639-1, e.g., 'pt').

    Returns:
        Translated text, or original text if source and target are the same.
        Returns "[Erro na tradução]" if translation fails.
    """
    if not text or not text.strip():
        return ""

    # If source and target languages are the same, return original text
    if source_lang == target_lang:
        return text

    # Handle special cases
    if source_lang == "silent" or source_lang == "error":
        return ""

    try:
        translator = GoogleTranslator(source_language=source_lang, target_language=target_lang)
        translated_text = translator.translate(text)
        return translated_text if translated_text else text

    except Exception as e:
        print(f"Translation error ({source_lang} → {target_lang}): {e}")
        return "[Erro na tradução]"


def get_language_name(lang_code: str) -> str:
    """
    Get human-readable language name from language code.

    Args:
        lang_code: ISO 639-1 language code.

    Returns:
        Language name, or the code itself if not recognized.
    """
    return LANGUAGE_NAMES.get(lang_code, lang_code)
