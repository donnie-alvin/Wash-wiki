import os
import sys

from flask import Flask, jsonify, render_template, request


CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(CURRENT_DIR)
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from logic.analytics import get_summary, log_event
from api.runtime import ensure_session_started, flow_manager


app = Flask(__name__)

from api.whatsapp import whatsapp_bp

app.register_blueprint(whatsapp_bp)


@app.post("/message")
def message():
    payload = request.get_json(silent=True) or {}
    session_id = payload.get("session_id")
    user_message = payload.get("user_message")

    if not session_id:
        return jsonify({"error": "session_id is required"}), 400

    if not isinstance(user_message, str) or not user_message.strip():
        return jsonify({"error": "user_message is required"}), 400

    user_message = user_message.strip()

    ensure_session_started(session_id)

    fm_response = flow_manager.process_message(session_id, user_message)
    intent_id = fm_response.get("intent_id")
    is_fallback = fm_response.get("is_fallback", False)
    is_escalation = fm_response.get("is_escalation", False)

    if intent_id is not None:
        log_event(
            "intent_matched",
            session_id,
            intent_id=intent_id,
            language=fm_response.get("language"),
        )
    if is_fallback is True:
        log_event("intent_not_matched", session_id)
    if is_escalation is True:
        log_event("escalation_triggered", session_id)
    if fm_response.get("is_ai") is True:
        log_event("intent_not_matched", session_id)
        log_event("ai_response", session_id, language=fm_response.get("language"))

    response_dict = {
        "response_text": fm_response.get("short"),
        "steps": fm_response.get("steps"),
        "warning": fm_response.get("warning"),
        "follow_up": fm_response.get("follow_up"),
        "language": fm_response.get("language"),
        "intent_id": intent_id,
        "is_fallback": is_fallback,
        "is_escalation": is_escalation,
        "is_ai": fm_response.get("is_ai", False),
        "topic_menu": fm_response.get("topic_menu"),
    }
    return jsonify(response_dict)


@app.get("/")
def index():
    return render_template("index.html")


@app.get("/health")
def health():
    return jsonify({"status": "ok"})


@app.get("/analytics")
def analytics():
    return jsonify(get_summary())


@app.post("/reload")
def reload_content():
    flow_manager.reload()
    return jsonify({"status": "reloaded"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
