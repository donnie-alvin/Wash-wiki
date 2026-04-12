import unittest


class IntentMatcherTests(unittest.TestCase):
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

    def test_unknown_input_returns_none(self):
        from logic import match_intent

        self.assertIsNone(match_intent("xyzzy foobar"))

    def test_fallback_shona_message(self):
        from logic import get_fallback

        self.assertEqual(
            get_fallback("shona")["message"],
            "Handina kunyatsonzwisisa mubvunzo wenyu. Munogona kubvunza nezvemvura, kugeza maoko, zvimbuzi, kana kudzivirira zvirwere.",
        )

    def test_fallback_english_message(self):
        from logic import get_fallback

        self.assertEqual(
            get_fallback("en")["message"],
            "I did not fully understand your question. You can ask about water safety, handwashing, toilets, or disease prevention.",
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
