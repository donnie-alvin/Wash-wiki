_SHONA_MSG = "Handina kunyatsonzwisisa mubvunzo wenyu. Munogona kubvunza nezvemvura, kugeza maoko, zvimbuzi, kana kudzivirira zvirwere."
_EN_MSG = "I did not fully understand your question. You can ask about water safety, handwashing, toilets, or disease prevention."
_TOPICS = ["Water Safety", "Handwashing", "Sanitation", "Disease Prevention"]


def get_fallback(language: str = "shona") -> dict:
    message = _EN_MSG if language == "en" else _SHONA_MSG
    return {
        "message": message,
        "short": message,
        "steps": _TOPICS,
        "topics": _TOPICS,
    }
