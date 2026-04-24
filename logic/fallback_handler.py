_SHONA_MSG = (
    "Handina kunzwisisa. Munogona kubvunza nezvemvura, kugeza maoko, "
    "zvimbuzi, kana kudzivirira zvirwere."
)
_EN_MSG = (
    "I didn't quite understand. You can ask me about:"
)
_TOPICS = ["Water Safety", "Handwashing", "Sanitation", "Disease Prevention"]


def get_fallback(language: str = "en") -> dict:
    message = _EN_MSG if language == "en" else _SHONA_MSG
    return {
        "message": message,
        "short": message,
        "steps": _TOPICS,
        "topics": _TOPICS,
    }
