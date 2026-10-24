"""
Text Cleaner Module
Cleans, normalizes, and prepares resume text for NLP processing and skill extraction.
Preserves critical technical markers like C++, C#, .NET, Node.js, and CI/CD while
removing noise, repeated spaces, and extraneous symbols.
"""

import re
from typing import Dict, List, Optional


# Preserved technical terms mapping to safe alphanumeric placeholders (no underscores)
PRESERVED_MARKERS = [
    (r"(?i)(?<![a-z0-9])c\+\+(?![a-z0-9])", "TECHTOKENCPP"),
    (r"(?i)(?<![a-z0-9])c\#(?![a-z0-9])", "TECHTOKENCSHARP"),
    (r"(?i)(?<![a-z0-9])\.net(?![a-z0-9])", "TECHTOKENDOTNET"),
    (r"(?i)(?<![a-z0-9])node\.js(?![a-z0-9])", "TECHTOKENNODEJS"),
    (r"(?i)(?<![a-z0-9])vue\.js(?![a-z0-9])", "TECHTOKENVUEJS"),
    (r"(?i)(?<![a-z0-9])react\.js(?![a-z0-9])", "TECHTOKENREACTJS"),
    (r"(?i)(?<![a-z0-9])ci/cd(?![a-z0-9])", "TECHTOKENCICD"),
    (r"(?i)(?<![a-z0-9])tcp/ip(?![a-z0-9])", "TECHTOKENTCPIP"),
    (r"(?i)(?<![a-z0-9])a/b\s+testing(?![a-z0-9])", "TECHTOKENABTESTING"),
    (r"(?i)(?<![a-z0-9])power\s+bi(?![a-z0-9])", "TECHTOKENPOWERBI"),
    (r"(?i)(?<![a-z0-9])scikit-learn(?![a-z0-9])", "TECHTOKENSCIKITLEARN"),
    (r"(?i)(?<![a-z0-9])hugging\s*face(?![a-z0-9])", "TECHTOKENHUGGINGFACE"),
]

# Reverse mapping to canonical tokens
REVERSE_MARKERS = [
    ("techtokencpp", "c++"),
    ("techtokencsharp", "c#"),
    ("techtokendotnet", ".net"),
    ("techtokennodejs", "node.js"),
    ("techtokenvuejs", "vue.js"),
    ("techtokenreactjs", "react.js"),
    ("techtokencicd", "ci/cd"),
    ("techtokentcpip", "tcp/ip"),
    ("techtokenabtesting", "a/b testing"),
    ("techtokenpowerbi", "power bi"),
    ("techtokenscikitlearn", "scikit-learn"),
    ("techtokenhuggingface", "hugging face"),
]


def clean_text(raw_text: Optional[str]) -> str:
    """
    Cleans raw resume text:
      1. Protects technical symbols (C++, C#, .NET, Node.js, CI/CD).
      2. Converts to lowercase.
      3. Strips URLs and email addresses.
      4. Strips non-alphanumeric noise while keeping protected markers.
      5. Restores technical markers into clean tokens.
      6. Normalizes consecutive whitespace.

    Args:
        raw_text: Raw string extracted from document.

    Returns:
        Cleaned, normalized lowercase string.
    """
    if not raw_text or not isinstance(raw_text, str):
        return ""

    text = raw_text

    # Protect technical markers by replacing with safe alphanumeric placeholders
    for pattern, placeholder in PRESERVED_MARKERS:
        text = re.sub(pattern, f" {placeholder} ", text)

    # Convert to lowercase
    text = text.lower()

    # Remove URLs (http, https, www)
    text = re.sub(r"https?://\S+|www\.\S+", " ", text)

    # Remove emails
    text = re.sub(r"\b[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}\b", " ", text)

    # Normalize special bullet points and symbols
    bullet_symbols = r"[\u2022\u2023\u25E6\u2043\u2219\u25CB\u25CF\u25A0\u25B6\u25C6\u2013\u2014\u2015\-–—•|*~_]"
    text = re.sub(bullet_symbols, " ", text)

    # Strip extraneous punctuation (leaving only alphanumeric and whitespace)
    # The placeholders like techtokencpp are purely [a-z0-9] and survive untouched
    text = re.sub(r"[^a-z0-9\s]", " ", text)

    # Restore preserved markers
    for placeholder, original in REVERSE_MARKERS:
        text = text.replace(placeholder, f" {original} ")

    # Normalize multiple whitespace, tabs, and newlines to single spaces
    text = re.sub(r"\s+", " ", text).strip()

    return text


def extract_metadata_contacts(raw_text: str) -> Dict[str, List[str]]:
    """
    Extracts candidate contact details like emails, phones, and GitHub/LinkedIn links.

    Args:
        raw_text: Uncleaned raw resume text.

    Returns:
        Dict with keys: emails, phones, links
    """
    if not raw_text:
        return {"emails": [], "phones": [], "links": []}

    # Emails
    emails = list(set(re.findall(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b", raw_text)))

    # Phone numbers
    phones = list(
        set(
            re.findall(
                r"(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}",
                raw_text,
            )
        )
    )

    # Links (GitHub, LinkedIn, Portfolio)
    links = list(
        set(
            re.findall(
                r"(?:https?://)?(?:www\.)?(?:linkedin\.com/in/[\w\-]+|github\.com/[\w\-]+)",
                raw_text,
                flags=re.IGNORECASE,
            )
        )
    )

    return {
        "emails": emails[:3],
        "phones": phones[:3],
        "links": links[:5],
    }
