import logging
import os

import requests
from flask import Blueprint, jsonify, request

from api.runtime import ensure_session_started, flow_manager
from api.whatsapp_formatter import format_whatsapp_reply
from logic.analytics import log_event


logger = logging.getLogger(__name__)

whatsapp_bp = Blueprint("whatsapp", __name__, url_prefix="/whatsapp")


@whatsapp_bp.get("/webhook")
def verify_webhook():
    hub_mode = request.args.get("hub.mode")
    hub_verify_token = request.args.get("hub.verify_token")
    hub_challenge = request.args.get("hub.challenge")

    if (
        hub_mode == "subscribe"
        and hub_verify_token == os.environ.get("WHATSAPP_VERIFY_TOKEN", "")
    ):
        return (hub_challenge or ""), 200, {"Content-Type": "text/plain; charset=utf-8"}

    return "Forbidden", 403


@whatsapp_bp.post("/webhook")
def handle_webhook():
    payload = request.get_json(silent=True) or {}

    try:
        value = payload["entry"][0]["changes"][0]["value"]
    except (KeyError, IndexError, TypeError):
        logger.warning("Received malformed WhatsApp webhook payload")
        return jsonify({"status": "ok"}), 200

    if "messages" not in value:
        return jsonify({"status": "ok"}), 200

    try:
        message = value["messages"][0]
        session_id = message["from"]
        user_message = message["text"]["body"]
    except (KeyError, IndexError, TypeError):
        logger.warning("Received unsupported WhatsApp message payload")
        return jsonify({"status": "ok"}), 200

    ensure_session_started(session_id)
    fm_response = flow_manager.process_message(session_id, user_message)
    reply_text = format_whatsapp_reply(fm_response)

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
    if is_fallback:
        log_event("intent_not_matched", session_id)
    if is_escalation:
        log_event("escalation_triggered", session_id)

    try:
        response = requests.post(
            f"https://graph.facebook.com/v18.0/{os.environ.get('WHATSAPP_PHONE_NUMBER_ID', '')}/messages",
            headers={
                "Authorization": f"Bearer {os.environ.get('WHATSAPP_ACCESS_TOKEN', '')}",
                "Content-Type": "application/json",
            },
            json={
                "messaging_product": "whatsapp",
                "to": session_id,
                "type": "text",
                "text": {"body": reply_text},
            },
            timeout=10,
        )
        if not response.ok:
            logger.warning(
                "Meta WhatsApp API returned %s: %s",
                response.status_code,
                response.text,
            )
    except requests.RequestException as exc:
        logger.warning("Meta WhatsApp API request failed: %s", exc)

    return jsonify({"status": "ok"}), 200
