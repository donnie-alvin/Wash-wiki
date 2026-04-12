import os
import unittest
from unittest.mock import Mock, patch

from api import app as api_app
from api import runtime as api_runtime
from api.whatsapp_formatter import format_whatsapp_reply


class WhatsAppWebhookTests(unittest.TestCase):
    def setUp(self):
        self.client = api_app.app.test_client()
        api_runtime.known_sessions.clear()

    @patch.dict(os.environ, {"WHATSAPP_VERIFY_TOKEN": "secret-token"}, clear=False)
    def test_webhook_verification_success(self):
        response = self.client.get(
            "/whatsapp/webhook",
            query_string={
                "hub.mode": "subscribe",
                "hub.verify_token": "secret-token",
                "hub.challenge": "challenge-123",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_data(as_text=True), "challenge-123")

    @patch.dict(os.environ, {"WHATSAPP_VERIFY_TOKEN": "secret-token"}, clear=False)
    def test_webhook_verification_wrong_token(self):
        response = self.client.get(
            "/whatsapp/webhook",
            query_string={
                "hub.mode": "subscribe",
                "hub.verify_token": "wrong-token",
                "hub.challenge": "challenge-123",
            },
        )

        self.assertEqual(response.status_code, 403)

    @patch("requests.post")
    @patch("api.runtime.log_event")
    def test_inbound_message_calls_process_message(self, mock_log_event, mock_post):
        mock_post.return_value = Mock(ok=True, status_code=200, text="ok")
        payload = {
            "entry": [
                {
                    "changes": [
                        {
                            "value": {
                                "messages": [
                                    {
                                        "from": "263771234567",
                                        "text": {"body": "How do I purify water?"},
                                    }
                                ]
                            }
                        }
                    ]
                }
            ]
        }

        with patch.object(
            api_app.flow_manager,
            "process_message",
            return_value={"short": "Boil the water first.", "language": "en"},
        ) as mock_process_message:
            response = self.client.post("/whatsapp/webhook", json=payload)

        self.assertEqual(response.status_code, 200)
        mock_process_message.assert_called_once_with(
            "263771234567", "How do I purify water?"
        )
        mock_post.assert_called_once()
        mock_log_event.assert_called_once_with("session_started", "263771234567")

    @patch("requests.post")
    @patch("api.runtime.log_event")
    def test_inbound_message_logs_session_started_once_per_sender(
        self, mock_log_event, mock_post
    ):
        mock_post.return_value = Mock(ok=True, status_code=200, text="ok")
        payload = {
            "entry": [
                {
                    "changes": [
                        {
                            "value": {
                                "messages": [
                                    {
                                        "from": "263771234567",
                                        "text": {"body": "Hello"},
                                    }
                                ]
                            }
                        }
                    ]
                }
            ]
        }

        with patch.object(
            api_app.flow_manager,
            "process_message",
            return_value={"short": "Hi there", "language": "en"},
        ) as mock_process_message:
            first_response = self.client.post("/whatsapp/webhook", json=payload)
            second_response = self.client.post("/whatsapp/webhook", json=payload)

        self.assertEqual(first_response.status_code, 200)
        self.assertEqual(second_response.status_code, 200)
        self.assertEqual(mock_process_message.call_count, 2)
        mock_log_event.assert_called_once_with("session_started", "263771234567")

    @patch("requests.post")
    def test_inbound_status_update_returns_200(self, mock_post):
        payload = {
            "entry": [
                {
                    "changes": [
                        {
                            "value": {
                                "statuses": [
                                    {"id": "wamid.123", "status": "delivered"}
                                ]
                            }
                        }
                    ]
                }
            ]
        }

        with patch.object(api_app.flow_manager, "process_message") as mock_process_message:
            response = self.client.post("/whatsapp/webhook", json=payload)

        self.assertEqual(response.status_code, 200)
        mock_process_message.assert_not_called()
        mock_post.assert_not_called()

    def test_format_whatsapp_reply_full(self):
        result = format_whatsapp_reply(
            {
                "response_text": "Use safe water.",
                "steps": ["Boil it", "Let it cool"],
                "warning": "Do not drink untreated water.",
                "follow_up": "Do you want storage tips?",
            }
        )

        self.assertEqual(
            result,
            "Use safe water.\n\n1. Boil it\n2. Let it cool\n\n⚠️ Do not drink untreated water.\n\nDo you want storage tips?",
        )

    def test_format_whatsapp_reply_truncation(self):
        result = format_whatsapp_reply({"response_text": "a" * 5000})

        self.assertEqual(len(result), 4096)
        self.assertEqual(result, "a" * 4096)


if __name__ == "__main__":
    unittest.main()
