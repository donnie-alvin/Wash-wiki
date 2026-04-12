class LanguageManager:
    def __init__(self, default: str = "shona") -> None:
        self._default = default
        self._sessions: dict[str, str] = {}

    def get_language(self, session_id: str) -> str:
        return self._sessions.get(session_id, self._default)

    def set_language(self, session_id: str, language: str) -> None:
        if language not in ("shona", "en"):
            raise ValueError("language must be 'shona' or 'en'")
        self._sessions[session_id] = language

    def detect_language_switch(self, user_input: str) -> str | None:
        lowered = user_input.lower()
        if any(phrase in lowered for phrase in ["english", "in english", "speak english"]):
            return "en"
        if any(phrase in lowered for phrase in ["shona", "in shona", "taura chishona"]):
            return "shona"
        return None
