import json
import string
from pathlib import Path

_CONTENT_DIR = Path(__file__).parent.parent / "content"
_CONTENT_FILES = (
    "water_safety.json",
    "handwashing.json",
    "sanitation.json",
    "disease_prevention.json",
)
_SUBSTITUTIONS = (
    ("water from the river", "river water"),
    ("water from river", "river water"),
    ("rwizi water", "river water"),
    ("mvura yerwizi", "river water"),
    ("mvura ye rwizi", "river water"),
    ("chimbuzi", "toilet"),
    ("latrine", "toilet"),
)


def _load_all_intents() -> list[dict]:
    intents: list[dict] = []
    for filename in _CONTENT_FILES:
        with (_CONTENT_DIR / filename).open("r", encoding="utf-8") as handle:
            intents.extend(json.load(handle))
    return intents


_ALL_INTENTS = _load_all_intents()


def reload_intents() -> None:
    global _ALL_INTENTS
    _ALL_INTENTS = _load_all_intents()


def _normalise(text: str) -> str:
    cleaned = text.lower()
    cleaned = cleaned.translate(str.maketrans("", "", string.punctuation))
    for raw, replacement in _SUBSTITUTIONS:
        cleaned = cleaned.replace(raw, replacement)
    return cleaned


def match_intent(user_input: str, language: str = "shona") -> dict | None:
    del language

    normalised_input = _normalise(user_input)

    for intent in _ALL_INTENTS:
        canonical = intent["canonical_question"]
        if (
            normalised_input == _normalise(canonical["en"])
            or normalised_input == _normalise(canonical["shona"])
        ):
            return intent

    for intent in _ALL_INTENTS:
        variations = intent["sample_variations"]["en"] + intent["sample_variations"]["shona"]
        for variation in variations:
            if normalised_input == _normalise(variation):
                return intent

    tokens = set(normalised_input.split())
    for intent in _ALL_INTENTS:
        normalised_tags = {_normalise(tag) for tag in intent["tags"]}
        if tokens & normalised_tags:
            return intent

    for intent in _ALL_INTENTS:
        for tag in intent["tags"]:
            if _normalise(tag) in normalised_input:
                return intent

    return None
