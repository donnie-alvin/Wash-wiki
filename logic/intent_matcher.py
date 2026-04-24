import json
import string
from difflib import SequenceMatcher
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
STRONG_SIGNAL_TAGS = {
    "water",
    "toilet",
    "soap",
    "sanitation",
    "wash",
    "sick",
    "cholera",
    "diarrhoea",
    "handwashing",
    "mvura",
    "chimbuzi",
    "sipo",
    "geza",
    "korora",
    "manyoka",
}
FUZZY_THRESHOLD = 0.75
GENERIC_TAG_TOKENS = {
    "and",
    "at",
    "can",
    "clean",
    "do",
    "drink",
    "for",
    "from",
    "get",
    "help",
    "how",
    "important",
    "is",
    "my",
    "of",
    "safe",
    "should",
    "the",
    "to",
    "what",
    "when",
    "why",
}


def _load_all_intents() -> list[dict]:
    intents: list[dict] = []
    for filename in _CONTENT_FILES:
        with (_CONTENT_DIR / filename).open("r", encoding="utf-8") as handle:
            intents.extend(json.load(handle))
    return intents


_ALL_INTENTS = _load_all_intents()


def get_all_intents() -> list[dict]:
    return _ALL_INTENTS


def reload_intents() -> None:
    global _ALL_INTENTS
    _ALL_INTENTS = _load_all_intents()


def _normalise(text: str) -> str:
    cleaned = text.lower()
    cleaned = cleaned.translate(str.maketrans("", "", string.punctuation))
    for raw, replacement in _SUBSTITUTIONS:
        cleaned = cleaned.replace(raw, replacement)
    return " ".join(cleaned.split())


def _keyword_metrics(intent: dict, normalised_input: str, input_tokens: set[str]) -> tuple[int, int, bool]:
    exact_tag_matches = 0
    phrase_matches = 0
    matched_tokens: set[str] = set()

    for tag in intent["tags"]:
        normalised_tag = _normalise(tag)
        if not normalised_tag:
            continue
        if normalised_input == normalised_tag:
            exact_tag_matches += 1
        elif len(normalised_tag) > 2 and normalised_tag in normalised_input:
            phrase_matches += 1

        matched_tokens.update(
            token
            for token in normalised_tag.split()
            if token in input_tokens and token not in GENERIC_TAG_TOKENS
        )

    strong_match = any(token in STRONG_SIGNAL_TAGS for token in matched_tokens)
    return exact_tag_matches, phrase_matches + len(matched_tokens), strong_match


def _match_exact_canonical_or_variation(normalised_input: str) -> dict | None:
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

    return None


def _match_tag_overlap(normalised_input: str) -> dict | None:
    input_tokens = set(normalised_input.split())
    best_match: dict | None = None
    best_exact_matches = 0
    best_phrase_score = 0
    best_strong_match = False

    for intent in _ALL_INTENTS:
        exact_matches, phrase_score, strong_match = _keyword_metrics(
            intent,
            normalised_input,
            input_tokens,
        )
        if (
            exact_matches > best_exact_matches
            or (
                exact_matches == best_exact_matches
                and phrase_score > best_phrase_score
            )
            or (
                exact_matches == best_exact_matches
                and phrase_score == best_phrase_score
                and strong_match
                and not best_strong_match
            )
        ):
            best_match = intent
            best_exact_matches = exact_matches
            best_phrase_score = phrase_score
            best_strong_match = strong_match

    if best_match is not None and (best_exact_matches > 0 or best_phrase_score > 0):
        return best_match

    return None


def _match_keyword_score(normalised_input: str) -> dict | None:
    input_tokens = set(normalised_input.split())
    best_scoring_intent: dict | None = None
    best_score = 0
    best_strong_match = False

    for intent in _ALL_INTENTS:
        _, score, strong_match = _keyword_metrics(intent, normalised_input, input_tokens)
        if score > best_score or (score == best_score and strong_match and not best_strong_match):
            best_scoring_intent = intent
            best_score = score
            best_strong_match = strong_match

    if best_scoring_intent is not None and (
        best_score >= 2 or (best_score >= 1 and best_strong_match)
    ):
        return best_scoring_intent

    return None


def _match_fuzzy(normalised_input: str) -> dict | None:
    best_fuzzy_intent: dict | None = None
    best_ratio = 0.0

    for intent in _ALL_INTENTS:
        candidates = [
            intent["canonical_question"]["en"],
            intent["canonical_question"]["shona"],
            *intent["sample_variations"]["en"],
            *intent["sample_variations"]["shona"],
        ]
        for candidate in candidates:
            ratio = SequenceMatcher(None, normalised_input, _normalise(candidate)).ratio()
            if ratio > best_ratio:
                best_ratio = ratio
                best_fuzzy_intent = intent

    if best_fuzzy_intent is not None and best_ratio >= FUZZY_THRESHOLD:
        return best_fuzzy_intent

    return None


def match_intent(user_input: str, language: str = "shona") -> dict | None:
    del language

    normalised_input = _normalise(user_input)
    return (
        _match_exact_canonical_or_variation(normalised_input)
        or _match_tag_overlap(normalised_input)
        or _match_keyword_score(normalised_input)
        or _match_fuzzy(normalised_input)
    )
