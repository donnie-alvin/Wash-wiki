# Wash Wiki Flask API

Lightweight Flask API serving the Wash Wiki chatbot.

## Installation

```bash
pip install -r api/requirements.txt
```

## Running

Run from the workspace root:

```bash
python api/app.py
```

## Web Chat

The web chat interface is available at `http://localhost:5000`.

## Endpoint Reference

| Method | Path | Description |
|---|---|---|
| `GET` | `/` | Serves the web chat interface |
| `GET` | `/health` | Returns `{"status": "ok"}` |
| `POST` | `/message` | Accepts `{session_id, user_message, language?}`, returns full response payload |

## WhatsApp Integration

| Method | Path | Description |
|---|---|---|
| `GET` | `/whatsapp/webhook` | Meta webhook verification endpoint |
| `POST` | `/whatsapp/webhook` | Receives inbound WhatsApp messages and sends chatbot replies via Meta |

Required environment variables:

- `WHATSAPP_VERIFY_TOKEN`
- `WHATSAPP_ACCESS_TOKEN`
- `WHATSAPP_PHONE_NUMBER_ID`

The WhatsApp webhook URL must be HTTPS and registered in the Meta Developer Console.

## POST /message Request Schema

| Field | Type | Required | Description |
|---|---|---|---|
| `session_id` | string | Yes | Unique session identifier for the conversation |
| `user_message` | string | Yes | The user's message text |
| `language` | string | No | Preferred language hint; defaults to `shona` |

## POST /message Response Schema

| Field | Type | Description |
|---|---|---|
| `response_text` | string | Primary chatbot response mapped from `short` |
| `steps` | array | Ordered instruction steps from the flow manager |
| `warning` | string or null | Warning text when applicable |
| `follow_up` | string or null | Follow-up prompt or clarifying response |
| `language` | string | Active language returned by the flow manager |
| `intent_id` | string | Intent identifier selected for the message |
| `is_fallback` | boolean | Indicates fallback handling |
| `is_escalation` | boolean | Indicates escalation handling |
| `topic_menu` | array | Suggested fallback topic options |

## Note

`logic/flow_manager.py` must be present (built separately). Run from the workspace root so the `logic` package is importable.
