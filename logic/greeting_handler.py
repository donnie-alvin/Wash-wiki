from __future__ import annotations

import string

_GREETING_KEYWORDS = {
    "hi",
    "hey",
    "hello",
    "good morning",
    "good afternoon",
    "good evening",
    "mhoro",
    "makadii",
    "ndeipi",
    "sawubona",
    "howzit",
    "sup",
    "yo",
    "greetings",
}


def _normalise(text: str) -> str:
    return " ".join(
        text.lower().translate(str.maketrans("", "", string.punctuation)).split()
    )


def is_greeting(user_input: str) -> bool:
    return _normalise(user_input) in _GREETING_KEYWORDS
