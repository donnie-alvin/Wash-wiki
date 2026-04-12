from logic.analytics import log_event
from logic.flow_manager import FlowManager


flow_manager = FlowManager()
known_sessions: set[str] = set()


def ensure_session_started(session_id: str) -> None:
    if session_id in known_sessions:
        return

    log_event("session_started", session_id)
    known_sessions.add(session_id)
