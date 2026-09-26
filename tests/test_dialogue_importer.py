import unittest

from brain.logic.dialogue_importer import (
    import_dialogue_batch,
    normalize_dialogue,
    validate_imported_slots,
)
from brain.logic.content_validation import ContentValidationError


class DialogueImporterTests(unittest.TestCase):
    def test_minimal_dialogue_is_normalized(self):
        raw = {
            "title": "Im Café",
            "section": "Im Café",
            "turns": [
                {"role": "teacher", "text": "Was möchtest du trinken?"},
                {
                    "role": "learner",
                    "expected": "Ich möchte einen Kaffee.",
                    "accepted": ["Einen Kaffee", "Ich möchte einen Kaffee."],
                },
            ],
        }
        d = normalize_dialogue(raw, level="A1", lesson=3)
        self.assertEqual(d["id"], "im-cafe")
        self.assertEqual(d["turns"][0]["role"], "nele")
        self.assertEqual(d["turns"][1]["role"], "student")
        self.assertIn("Einen Kaffee", d["turns"][1]["accepted_patterns"])
        self.assertTrue(d["turns"][1]["expected_intent"])
        self.assertIn("combine_unrelated_topics", d["forbidden_variations"])

    def test_existing_semantic_fields_are_preserved(self):
        raw = {
            "id": "origin",
            "title": "Herkunft",
            "section": "Herkunft",
            "topic": "Herkunft",
            "register": "formal",
            "max_turns": 4,
            "turns": [
                {"role": "nele", "text": "Woher kommen Sie?", "intent": "ask_origin"},
                {
                    "role": "student",
                    "expected_intent": "give_origin",
                    "expected": "Ich komme aus Polen.",
                    "accepted_patterns": ["Ich komme aus {country}", "{country}"],
                },
            ],
            "slots": {"country": "Polen"},
        }
        d = normalize_dialogue(raw)
        self.assertEqual(d["register"], "formal")
        self.assertEqual(d["max_turns"], 4)
        self.assertEqual(d["turns"][0]["intent"], "ask_origin")
        self.assertEqual(d["turns"][1]["expected_intent"], "give_origin")
        self.assertTrue(validate_imported_slots(d))

    def test_undefined_slot_is_rejected(self):
        raw = {
            "title": "Herkunft",
            "section": "Herkunft",
            "turns": [
                {"role": "nele", "text": "Woher kommst du?"},
                {
                    "role": "student",
                    "expected": "Ich komme aus Polen.",
                    "accepted_patterns": ["Ich komme aus {country}"],
                },
            ],
        }
        d = normalize_dialogue(raw)
        with self.assertRaises(ContentValidationError):
            validate_imported_slots(d)

    def test_importer_does_not_invent_teaching_content(self):
        raw = {
            "title": "Hallo",
            "section": "Hallo",
            "turns": [
                {"role": "nele", "text": "Hallo!"},
                {"role": "student", "expected": "Hallo!"},
            ],
        }
        d = normalize_dialogue(raw)
        self.assertNotIn("grammar", d)
        self.assertNotIn("vocabulary", d)
        self.assertNotIn("learning_goals", d)


    def test_batch_keeps_valid_and_rejects_invalid_dialogue(self):
        batch = [
            {
                "title": "Begrüßung",
                "section": "Hallo",
                "turns": [
                    {"role": "nele", "text": "Hallo! Wie heißt du?"},
                    {"role": "student", "expected": "Ich heiße Moni."},
                ],
            },
            {
                "title": "Kaputter Dialog",
                "section": "Herkunft",
                "turns": [
                    {"role": "nele", "text": "Woher kommst du?"},
                    {
                        "role": "student",
                        "expected": "Ich komme aus Polen.",
                        "accepted_patterns": ["Ich komme aus {country}"],
                    },
                ],
            },
        ]
        report = import_dialogue_batch(batch, level="A1", lesson=1)
        self.assertEqual(report["accepted_count"], 1)
        self.assertEqual(report["rejected_count"], 1)
        self.assertFalse(report["ok"])
        self.assertEqual(report["accepted"][0]["id"], "begruessung")
        self.assertIn("undefined slots", report["rejected"][0]["reason"])

    def test_batch_rejects_duplicate_ids(self):
        raw = {
            "id": "hello",
            "title": "Hallo",
            "section": "Hallo",
            "turns": [
                {"role": "nele", "text": "Hallo!"},
                {"role": "student", "expected": "Hallo!"},
            ],
        }
        report = import_dialogue_batch([raw, raw])
        self.assertEqual(report["accepted_count"], 1)
        self.assertEqual(report["rejected_count"], 1)
        self.assertIn("Duplicate dialogue id", report["rejected"][0]["reason"])


if __name__ == "__main__":
    unittest.main()
