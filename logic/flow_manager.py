"""Conversation flow manager for multi-turn chatbot sessions."""

from __future__ import annotations

from logic.decision_trees import get_follow_up_question, resolve_branch
from logic.fallback_handler import get_fallback
from logic.intent_matcher import match_intent, reload_intents
from logic.language_manager import LanguageManager
from logic.response_builder import build_response

ESCALATION_KEYWORDS = {
    "severe",
    "dying",
    "very sick",
    "hospital",
    "emergency",
    "ndoda rubatsiro",
    "ndirwara chaizvo",
    "ndoda chipatara",
}

ESCALATION_MESSAGES = {
    "shona": (
        "Zvirwere izvi zvinoda rubatsiro rwechipatara. "
        "Endai kuchipatara chepedyo kana kubata mushandi weutano."
    ),
    "en": "This sounds serious. Please go to your nearest clinic or contact a health worker.",
}

TOPIC_MAP = {
    "water safety": [
        "Is my water safe to drink?",
        "Can I drink river water?",
        "How can I treat water at home?",
        "How can I clean dirty water?",
    ],
    "mvura yakachengeteka": [
        "Is my water safe to drink?",
        "Can I drink river water?",
        "How can I treat water at home?",
        "How can I clean dirty water?",
    ],
    "handwashing": [
        "Why is handwashing important?",
        "When should I wash my hands?",
        "How do I wash my hands properly?",
        "What should I do if I do not have soap?",
    ],
    "kugeza maoko": [
        "Why is handwashing important?",
        "When should I wash my hands?",
        "How do I wash my hands properly?",
        "What should I do if I do not have soap?",
    ],
    "sanitation": [
        "What is sanitation?",
        "Why is sanitation important?",
        "Why should I use a toilet?",
        "How can I keep my toilet clean?",
    ],
    "utachiona": [
        "What is sanitation?",
        "Why is sanitation important?",
        "Why should I use a toilet?",
        "How can I keep my toilet clean?",
    ],
    "disease prevention": [
        "How can I protect myself from diseases?",
        "Why do diseases increase during the rainy season?",
        "What should I do during a cholera outbreak?",
    ],
    "kudzivirira zvirwere": [
        "How can I protect myself from diseases?",
        "Why do diseases increase during the rainy season?",
        "What should I do during a cholera outbreak?",
    ],
}

LANGUAGE_SWITCH_ACK = {
    "en": "Switched to English.",
    "shona": "Tichataura muShona.",
}


class FlowManager:
    def __init__(self) -> None:
        self._sessions: dict[str, dict] = {}
        self._lang_manager = LanguageManager()

    def reload(self) -> None:
        reload_intents()

    def _get_session(self, session_id: str) -> dict:
        if session_id not in self._sessions:
            self._sessions[session_id] = {
                "language": "shona",
                "awaiting_follow_up": None,
                "follow_up_context": None,
                "last_intent_id": None,
            }
        return self._sessions[session_id]

    def _check_escalation(self, user_input: str) -> bool:
        lowered_input = user_input.lower()
        return any(keyword in lowered_input for keyword in ESCALATION_KEYWORDS)

    def _check_topic_menu(self, user_input: str) -> list[str] | None:
        return TOPIC_MAP.get(user_input.lower())

    def _build_output(
        self,
        response: dict,
        session: dict,
        *,
        is_fallback: bool = False,
        is_escalation: bool = False,
        topic_menu=None,
    ) -> dict:
        output = dict(response)
        output["language"] = session["language"]
        output["intent_id"] = session["last_intent_id"]
        output["is_fallback"] = is_fallback
        output["is_escalation"] = is_escalation
        output["topic_menu"] = topic_menu
        return output

    def process_message(self, session_id: str, user_input: str) -> dict:
        session = self._get_session(session_id)

        language = self._lang_manager.detect_language_switch(user_input)
        if language:
            self._lang_manager.set_language(session_id, language)
            session["language"] = language
            session["last_intent_id"] = None
            return self._build_output(
                {"short": LANGUAGE_SWITCH_ACK.get(language, LANGUAGE_SWITCH_ACK["en"])},
                session,
            )

        topic_menu = self._check_topic_menu(user_input)
        if topic_menu is not None:
            session["last_intent_id"] = None
            return self._build_output(
                {
                    "short": "Here are questions you can ask:",
                    "steps": topic_menu,
                },
                session,
                topic_menu=topic_menu,
            )

        if self._check_escalation(user_input):
            session["awaiting_follow_up"] = None
            session["follow_up_context"] = None
            session["last_intent_id"] = None
            return self._build_output(
                {
                    "short": ESCALATION_MESSAGES.get(
                        session["language"],
                        ESCALATION_MESSAGES["en"],
                    ),
                },
                session,
                is_escalation=True,
            )

        if session["awaiting_follow_up"] is not None:
            branch = resolve_branch(session["awaiting_follow_up"], user_input)
            if branch is not None:
                session["last_intent_id"] = session["awaiting_follow_up"]
                session["awaiting_follow_up"] = None
                session["follow_up_context"] = None
                return self._build_output(branch, session)

            return self._build_output(
                {"short": get_follow_up_question(session["awaiting_follow_up"])},
                session,
            )

        intent = match_intent(user_input, session["language"])
        if intent is not None:
            response = build_response(intent, session["language"])
            session["last_intent_id"] = intent["intent_id"]
            if response.get("follow_up") is not None:
                session["awaiting_follow_up"] = intent["intent_id"]
                session["follow_up_context"] = {"intent_id": intent["intent_id"]}
                follow_up = get_follow_up_question(intent["intent_id"])
                if follow_up is not None:
                    response = dict(response)
                    response["follow_up"] = follow_up
            return self._build_output(response, session)

        fallback = get_fallback(session["language"])
        fallback_topics = fallback.get("topics") or fallback.get("steps") or list(TOPIC_MAP.keys())
        session["last_intent_id"] = None
        return self._build_output(
            fallback,
            session,
            is_fallback=True,
            topic_menu=fallback_topics,
        )
