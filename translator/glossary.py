"""Glossary management - protects domain-specific terms from incorrect translation."""

import re
from typing import Dict, List, Optional


# Built-in glossaries for different domains
GLOSSARIES = {
    "tech": {
        "pipeline": "pipeline",
        "deploy": "deploy",
        "sprint": "sprint",
        "backend": "backend",
        "frontend": "frontend",
        "api": "API",
        "bug": "bug",
        "feature": "feature",
        "pull request": "pull request",
        "merge": "merge",
        "staging": "staging",
        "production": "production",
        "repository": "repository",
        "commit": "commit",
        "branch": "branch",
        "refactor": "refactor",
        "database": "database",
        "cache": "cache",
        "server": "server",
        "client": "client"
    },
    "finance": {
        "revenue": "revenue",
        "churn": "churn",
        "arr": "ARR",
        "mrr": "MRR",
        "runway": "runway",
        "burn rate": "burn rate",
        "equity": "equity",
        "cap table": "cap table",
        "term sheet": "term sheet",
        "due diligence": "due diligence",
        "valuation": "valuation",
        "dilution": "dilution",
        "vesting": "vesting"
    },
    "legal": {
        "compliance": "compliance",
        "liability": "liability",
        "nda": "NDA",
        "clause": "clause",
        "indemnity": "indemnity",
        "jurisdiction": "jurisdiction",
        "arbitration": "arbitration",
        "contract": "contract",
        "agreement": "agreement",
        "defendant": "defendant",
        "plaintiff": "plaintiff"
    },
    "none": {}
}


def apply_glossary(text: str, profile: Optional[str] = None, custom_terms: Optional[Dict[str, str]] = None) -> str:
    """
    Protect glossary terms by wrapping them with [[brackets]].

    Args:
        text: Input text
        profile: Glossary profile name (tech, finance, legal, none)
        custom_terms: Custom glossary terms to protect

    Returns:
        Text with protected terms wrapped in [[brackets]]
    """
    if not text:
        return text

    # Get glossary for profile
    glossary = {}
    if profile and profile in GLOSSARIES:
        glossary = GLOSSARIES[profile].copy()

    # Merge with custom terms
    if custom_terms:
        glossary.update(custom_terms)

    if not glossary:
        return text

    result = text
    # Sort by length descending to replace longer terms first
    sorted_terms = sorted(glossary.keys(), key=len, reverse=True)

    for term in sorted_terms:
        # Case-insensitive replacement with word boundaries
        pattern = r'\b' + re.escape(term) + r'\b'
        replacement = f"[[{term}]]"
        result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)

    return result


def restore_glossary(text: str) -> str:
    """
    Remove [[brackets]] protecting glossary terms.

    Args:
        text: Text with protected terms

    Returns:
        Text with brackets removed
    """
    if not text:
        return text

    # Remove [[...]] wrappers
    result = re.sub(r'\[\[([^\]]+)\]\]', r'\1', text)
    return result


def merge_glossary(base_profile: Optional[str], speaker_glossary: Optional[Dict[str, str]]) -> Dict[str, str]:
    """
    Merge built-in glossary with speaker-extracted terms.

    Args:
        base_profile: Built-in glossary profile (tech, finance, legal, none)
        speaker_glossary: Speaker-specific glossary terms

    Returns:
        Merged glossary dictionary
    """
    glossary = {}

    # Start with built-in profile
    if base_profile and base_profile in GLOSSARIES:
        glossary = GLOSSARIES[base_profile].copy()

    # Merge speaker glossary (speaker terms take precedence)
    if speaker_glossary:
        glossary.update(speaker_glossary)

    return glossary


def get_profile_names() -> List[str]:
    """
    Get list of available glossary profiles.

    Returns:
        List of profile names
    """
    return list(GLOSSARIES.keys())
