import json
import os
import tempfile
import unittest

from logic import analytics


class AnalyticsTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.log_file = os.path.join(self.temp_dir.name, "events.jsonl")
        self.original_log_file = analytics.LOG_FILE
        analytics.LOG_FILE = self.log_file

    def tearDown(self):
        analytics.LOG_FILE = self.original_log_file
        self.temp_dir.cleanup()

    def test_log_event_writes_valid_json_line(self):
        analytics.log_event("intent_matched", "session-1", intent_id="water_safe", language="en")

        with open(self.log_file, "r", encoding="utf-8") as handle:
            line = handle.readline()

        payload = json.loads(line)
        self.assertEqual(payload["event_type"], "intent_matched")
        self.assertEqual(payload["session_id"], "session-1")
        self.assertEqual(payload["intent_id"], "water_safe")
        self.assertEqual(payload["language"], "en")
        self.assertIn("timestamp", payload)

    def test_get_summary_intent_match_rate(self):
        events = [
            {"event_type": "intent_matched", "session_id": "s1", "intent_id": "a"},
            {"event_type": "intent_matched", "session_id": "s1", "intent_id": "a"},
            {"event_type": "intent_matched", "session_id": "s2", "intent_id": "b"},
            {"event_type": "intent_not_matched", "session_id": "s3"},
        ]
        self._write_events(events)

        summary = analytics.get_summary()
        self.assertEqual(summary["intent_match_rate"], 0.75)

    def test_get_summary_top_intents(self):
        events = [
            {"event_type": "intent_matched", "session_id": "s1", "intent_id": "water_safe"},
            {"event_type": "intent_matched", "session_id": "s2", "intent_id": "water_safe"},
            {"event_type": "intent_matched", "session_id": "s3", "intent_id": "handwashing"},
        ]
        self._write_events(events)

        summary = analytics.get_summary()
        self.assertEqual(
            summary["top_intents"],
            [
                {"intent_id": "water_safe", "count": 2},
                {"intent_id": "handwashing", "count": 1},
            ],
        )

    def test_get_summary_language_breakdown(self):
        events = [
            {"event_type": "language_selected", "session_id": "s1", "language": "en"},
            {"event_type": "language_selected", "session_id": "s2", "language": "shona"},
            {"event_type": "language_selected", "session_id": "s3", "language": "shona"},
        ]
        self._write_events(events)

        summary = analytics.get_summary()
        self.assertEqual(summary["language_breakdown"], {"en": 1, "shona": 2})

    def _write_events(self, events):
        os.makedirs(os.path.dirname(self.log_file), exist_ok=True)
        with open(self.log_file, "w", encoding="utf-8") as handle:
            for event in events:
                handle.write(json.dumps(event) + "\n")


if __name__ == "__main__":
    unittest.main()
