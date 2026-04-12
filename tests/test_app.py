import unittest
from unittest.mock import patch

from api import app as api_app
from api import runtime as api_runtime


class AppTests(unittest.TestCase):
    def setUp(self):
        self.client = api_app.app.test_client()
        api_runtime.known_sessions.clear()

    @patch.object(api_app, "ensure_session_started")
    @patch.object(api_app, "log_event")
    @patch.object(api_app.flow_manager, "process_message")
    def test_message_endpoint_returns_is_ai_for_ai_handled_reply(
        self,
        mock_process_message,
        mock_log_event,
        mock_ensure_session_started,
    ):
        del mock_ensure_session_started
        mock_process_message.return_value = {
            "short": "AI reply",
            "steps": None,
            "warning": None,
            "follow_up": None,
            "language": "en",
            "intent_id": None,
            "is_fallback": False,
            "is_escalation": False,
            "is_ai": True,
            "topic_menu": None,
        }

        response = self.client.post(
            "/message",
            json={"session_id": "session-ai-api-2", "user_message": "something unrelated"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.get_json()["is_ai"])
        mock_log_event.assert_any_call("intent_not_matched", "session-ai-api-2")
        mock_log_event.assert_any_call("ai_response", "session-ai-api-2", language="en")


if __name__ == "__main__":
    unittest.main()
