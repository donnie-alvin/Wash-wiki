import json
import os
import threading
from collections import Counter
from datetime import UTC, datetime


LOG_FILE = os.environ.get("ANALYTICS_LOG", "logs/events.jsonl")
_LOG_LOCK = threading.Lock()


def log_event(event_type: str, session_id: str, **kwargs):
    record = {
        "event_type": event_type,
        "session_id": session_id,
        "timestamp": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
    }
    record.update(kwargs)

    log_dir = os.path.dirname(LOG_FILE) or "logs"
    os.makedirs(log_dir, exist_ok=True)

    with _LOG_LOCK:
        with open(LOG_FILE, "a", encoding="utf-8") as handle:
            handle.write(json.dumps(record) + "\n")


def get_summary() -> dict:
    summary = {
        "total_sessions": 0,
        "total_messages": 0,
        "intent_match_rate": 0.0,
        "fallback_rate": 0.0,
        "top_intents": [],
        "language_breakdown": {},
        "escalations": 0,
    }

    if not os.path.exists(LOG_FILE):
        return summary

    session_ids = set()
    intent_counts = Counter()
    language_counts = Counter()
    matched = 0
    not_matched = 0
    escalations = 0

    with open(LOG_FILE, "r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue

            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                continue

            event_type = event.get("event_type")

            if event_type == "session_started" and event.get("session_id"):
                session_ids.add(event["session_id"])
            elif event_type == "intent_matched":
                matched += 1
                intent_id = event.get("intent_id")
                if intent_id:
                    intent_counts[intent_id] += 1
            elif event_type == "intent_not_matched":
                not_matched += 1
            elif event_type == "language_selected":
                language = event.get("language")
                if language:
                    language_counts[language] += 1
            elif event_type == "escalation_triggered":
                escalations += 1

    total_messages = matched + not_matched
    summary["total_sessions"] = len(session_ids)
    summary["total_messages"] = total_messages
    summary["intent_match_rate"] = matched / total_messages if total_messages else 0.0
    summary["fallback_rate"] = not_matched / total_messages if total_messages else 0.0
    summary["top_intents"] = [
        {"intent_id": intent_id, "count": count}
        for intent_id, count in intent_counts.most_common(10)
    ]
    summary["language_breakdown"] = dict(language_counts)
    summary["escalations"] = escalations
    return summary
