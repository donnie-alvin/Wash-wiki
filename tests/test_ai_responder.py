import unittest
from unittest.mock import MagicMock, patch

from api import app as api_app
from api import runtime as api_runtime
from logic.ai_responder import get_ai_response
from logic.flow_manager import FlowManager


class TestAIResponder(unittest.TestCase):
    @patch.dict("os.environ", {"AI_ENABLED": "false", "OPENAI_API_KEY": "test-key"}, clear=False)
    def test_ai_disabled_returns_none(self):
        response = get_ai_response("Can I drink this water?", "en", [])
        self.assertIsNone(response)

    @patch.dict("os.environ", {"AI_ENABLED": "true"}, clear=True)
    def test_ai_key_missing_returns_none(self):
        response = get_ai_response("Can I drink this water?", "en", [])
        self.assertIsNone(response)

    @patch.dict("os.environ", {"AI_ENABLED": "true", "OPENAI_API_KEY": "test-key"}, clear=True)
    @patch("logic.ai_responder.openai.OpenAI", side_effect=Exception("API error"))
    def test_ai_api_error_returns_none(self, mock_openai):
        del mock_openai
        response = get_ai_response("Can I drink this water?", "en", [])
        self.assertIsNone(response)

    @patch.dict("os.environ", {"AI_ENABLED": "true", "OPENAI_API_KEY": "test-key"}, clear=True)
    @patch("logic.ai_responder.openai.OpenAI")
    def test_ai_returns_string_on_success(self, mock_openai):
        mock_completion = MagicMock()
        mock_completion.choices[0].message.content = "Boil your water."
        mock_openai.return_value.chat.completions.create.return_value = mock_completion

        response = get_ai_response("Can I drink this water?", "en", [])

        self.assertEqual(response, "Boil your water.")

    @patch.dict("os.environ", {"AI_ENABLED": "true", "OPENAI_API_KEY": "test-key"}, clear=True)
    @patch("logic.ai_responder.openai.OpenAI")
    def test_ai_uses_required_safety_prompt(self, mock_openai):
        mock_completion = MagicMock()
        mock_completion.choices[0].message.content = "Boil your water."
        mock_openai.return_value.chat.completions.create.return_value = mock_completion

        get_ai_response("Can I drink this water?", "shona", [])

        _, kwargs = mock_openai.return_value.chat.completions.create.call_args
        system_prompt = kwargs["messages"][0]["content"]
        self.assertEqual(
            system_prompt,
            (
                "You are a sanitation and water safety assistant for rural communities in "
                "Bikita District, Zimbabwe. You help people understand safe water practices, "
                "handwashing, sanitation, and disease prevention. Answer only from the "
                "knowledge base provided. Keep answers to 1 to 3 short sentences. Use simple "
                "words. Do not diagnose illness. Do not replace a health worker. If someone "
                "describes a severe emergency, tell them to go to the nearest clinic. If the "
                "question is outside the knowledge base, say you cannot help with that and "
                "suggest they ask about water safety, handwashing, sanitation, or disease "
                "prevention. Respond in Shona language."
            ),
        )


class TestFlowManagerAI(unittest.TestCase):
    def setUp(self):
        language_manager_patcher = patch("logic.flow_manager.LanguageManager")
        self.addCleanup(language_manager_patcher.stop)
        self.mock_language_manager_cls = language_manager_patcher.start()
        self.mock_language_manager = self.mock_language_manager_cls.return_value
        self.mock_language_manager.detect_language_switch.return_value = None
        self.manager = FlowManager()

    @patch("logic.flow_manager.get_ai_response", return_value="Test AI reply")
    @patch("logic.flow_manager.match_intent", return_value=None)
    def test_flow_manager_uses_ai_on_no_match(self, mock_match_intent, mock_get_ai_response):
        del mock_match_intent
        del mock_get_ai_response

        response = self.manager.process_message("session-ai-1", "something unrelated")

        self.assertEqual(response["short"], "Test AI reply")
        self.assertTrue(response["is_ai"])
        self.assertFalse(response["is_fallback"])

    @patch("logic.flow_manager.get_fallback")
    @patch("logic.flow_manager.get_ai_response", return_value=None)
    @patch("logic.flow_manager.match_intent", return_value=None)
    def test_flow_manager_falls_back_when_ai_returns_none(
        self,
        mock_match_intent,
        mock_get_ai_response,
        mock_get_fallback,
    ):
        del mock_match_intent
        del mock_get_ai_response
        mock_get_fallback.return_value = {
            "short": "I did not understand that.",
            "steps": [],
            "warning": None,
            "follow_up": None,
        }

        response = self.manager.process_message("session-ai-2", "something unrelated")

        self.assertTrue(response["is_fallback"])
        self.assertFalse(response.get("is_ai", False))


class TestMessageApiAI(unittest.TestCase):
    def setUp(self):
        self.client = api_app.app.test_client()
        api_runtime.known_sessions.clear()

    @patch.object(api_app, "ensure_session_started")
    @patch.object(api_app.flow_manager, "process_message")
    def test_message_endpoint_includes_is_ai_when_ai_handles_request(
        self,
        mock_process_message,
        mock_ensure_session_started,
    ):
        del mock_ensure_session_started
        mock_process_message.return_value = {
            "short": "Test AI reply",
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
            json={"session_id": "session-ai-api-1", "user_message": "something unrelated"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["is_ai"], True)


if __name__ == "__main__":
    unittest.main()
