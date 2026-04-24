import os
import unittest
from unittest.mock import patch

from api import app as api_app
from api import runtime as api_runtime


class AppTests(unittest.TestCase):
    def setUp(self):
        self.client = api_app.app.test_client()
        api_runtime.known_sessions.clear()

    def test_index_endpoint_renders_template_from_repo_root_import(self):
        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Wash Wiki Chat", response.data)
        self.assertIn(b"quick-reply-btn", response.data)

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

    def test_index_route_renders_from_api_templates_directory(self):
        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertTrue(os.path.isabs(api_app.app.template_folder))
        self.assertTrue(api_app.app.template_folder.endswith("api/templates"))

    def test_favicon_route_serves_static_icon(self):
        response = self.client.get("/favicon.ico")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, "image/svg+xml")
        self.assertIn(b"<svg", response.data)


if __name__ == "__main__":
    unittest.main()
