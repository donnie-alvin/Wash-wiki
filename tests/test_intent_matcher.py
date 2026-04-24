import unittest
from unittest.mock import patch


class IntentMatcherTests(unittest.TestCase):
    def test_greeting_handler_matches_whole_input(self):
        from logic import is_greeting

        self.assertTrue(is_greeting("Hello!!!"))
        self.assertTrue(is_greeting(" good morning "))
        self.assertFalse(is_greeting("hello there"))

    def test_canonical_match_english(self):
        from logic import match_intent

        intent = match_intent("Can I drink river water?")
        self.assertIsNotNone(intent)
        self.assertEqual(intent["intent_id"], "water_river_safe")

    def test_canonical_match_shona(self):
        from logic import match_intent

        intent = match_intent("Ndinganwa mvura yerwizi here?")
        self.assertIsNotNone(intent)
        self.assertEqual(intent["intent_id"], "water_river_safe")

    def test_variation_match(self):
        from logic import match_intent

        intent = match_intent("Is river water safe to drink?")
        self.assertIsNotNone(intent)
        self.assertEqual(intent["intent_id"], "water_river_safe")

    def test_normalise_rwizi_water(self):
        from logic import match_intent

        intent = match_intent("rwizi water")
        self.assertIsNotNone(intent)
        self.assertEqual(intent["intent_id"], "water_river_safe")

    def test_normalise_mvura_yerwizi(self):
        from logic import match_intent

        intent = match_intent("mvura yerwizi")
        self.assertIsNotNone(intent)
        self.assertEqual(intent["intent_id"], "water_river_safe")

    def test_tag_match_river(self):
        from logic import match_intent

        intent = match_intent("river")
        self.assertIsNotNone(intent)
        self.assertEqual(intent["intent_id"], "water_river_safe")

    def test_keyword_scoring_prefers_highest_score(self):
        from logic.intent_matcher import match_intent

        intents = [
            {
                "intent_id": "first",
                "canonical_question": {"en": "unused", "shona": "unused"},
                "sample_variations": {"en": [], "shona": []},
                "tags": ["clean container"],
            },
            {
                "intent_id": "second",
                "canonical_question": {"en": "unused", "shona": "unused"},
                "sample_variations": {"en": [], "shona": []},
                "tags": ["clean container", "covered storage"],
            },
        ]

        with patch("logic.intent_matcher._ALL_INTENTS", intents):
            intent = match_intent("the container should stay clean and storage covered")

        self.assertIsNotNone(intent)
        self.assertEqual(intent["intent_id"], "second")

    def test_keyword_scoring_accepts_strong_signal_tag(self):
        from logic.intent_matcher import match_intent

        intents = [
            {
                "intent_id": "strong",
                "canonical_question": {"en": "unused", "shona": "unused"},
                "sample_variations": {"en": [], "shona": []},
                "tags": ["clean soap"],
            }
        ]

        with patch("logic.intent_matcher._ALL_INTENTS", intents):
            intent = match_intent("I need soap that is clean today")

        self.assertIsNotNone(intent)
        self.assertEqual(intent["intent_id"], "strong")

    def test_fuzzy_match_handles_typo(self):
        from logic import match_intent

        intent = match_intent("Can I drink rivier water?")
        self.assertIsNotNone(intent)
        self.assertEqual(intent["intent_id"], "water_river_safe")

    def test_keyword_scoring_matches_single_topic_keyword(self):
        from logic import match_intent

        intent = match_intent("water")
        self.assertIsNotNone(intent)
        self.assertEqual(intent["intent_id"], "water_safe")

    def test_keyword_scoring_matches_toilet(self):
        from logic import match_intent

        intent = match_intent("toilet")
        self.assertIsNotNone(intent)
        self.assertEqual(intent["intent_id"], "toilet_why")

    def test_fuzzy_match_handles_boil_typo_phrase(self):
        from logic import match_intent

        intent = match_intent("how do i boil watter")
        self.assertIsNotNone(intent)
        self.assertEqual(intent["intent_id"], "water_boil_why")

    def test_unknown_input_returns_none(self):
        from logic import match_intent

        self.assertIsNone(match_intent("xyzzy foobar"))

    def test_fallback_shona_message(self):
        from logic import get_fallback

        self.assertEqual(
            get_fallback("shona")["message"],
            "Handina kunyatsonzwisisa. Munogona kubvunza nezvemvura yakachengeteka, kugeza maoko, sanitation, kana kudzivirira zvirwere.",
        )

    def test_fallback_english_message(self):
        from logic import get_fallback

        self.assertEqual(
            get_fallback("en")["message"],
            "I didn't quite understand that. You can ask me about water safety, handwashing, sanitation, or disease prevention.",
        )

    def test_language_manager_default(self):
        from logic import LanguageManager

        self.assertEqual(LanguageManager().get_language("s1"), "shona")

    def test_language_manager_switch_english(self):
        from logic import LanguageManager

        manager = LanguageManager()
        self.assertEqual(manager.detect_language_switch("speak English"), "en")
        manager.set_language("s1", "en")
        self.assertEqual(manager.get_language("s1"), "en")

    def test_response_builder_language_fields(self):
        from logic import build_response, match_intent

        intent = match_intent("Can I drink river water?")
        self.assertIsNotNone(intent)
        self.assertEqual(
            build_response(intent, "en")["short"],
            intent["answer_short"]["en"],
        )
        self.assertEqual(
            build_response(intent, "shona")["short"],
            intent["answer_short"]["shona"],
        )


if __name__ == "__main__":
    unittest.main()
