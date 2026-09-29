import unittest

from brain.logic.memory import complete_state, create_empty_state
from brain.logic.personal_sentences import (
    ensure_personal_sentence_memory,
    handle_personal_sentence,
    get_personal_sentence_catalog,
    validate_personal_sentence_catalog,
)


class PersonalSentencesTests(unittest.TestCase):
    def test_catalogue_is_valid_and_extendable(self):
        self.assertTrue(validate_personal_sentence_catalog())
        catalogue = get_personal_sentence_catalog()
        self.assertGreaterEqual(len(catalogue), 6)
        self.assertTrue(all(item.get("practice_prompt") for item in catalogue))

    def test_work_questions_keep_nele_in_tutor_role(self):
        state = create_empty_state()
        today = handle_personal_sentence("Arbeitest du heute?", state, mode="free")
        self.assertIn("Deutschlernen", today["reply"])
        self.assertNotIn("einiges zu tun", today["reply"])

        sunday = handle_personal_sentence("Arbeitest du am Sonntag?", state, mode="free")
        self.assertIn("Deutschlernen", sunday["reply"])
        self.assertNotIn("habe ich frei", sunday["reply"])

    def test_known_sentence_is_recognized_and_recorded(self):
        state = create_empty_state()
        result = handle_personal_sentence(
            "Ich kümmere mich darum.",
            state,
            mode="free",
        )
        self.assertIsNotNone(result)
        self.assertIn("Danke", result["reply"])
        item = state["personal_sentences"]["items"]["ich_kuemmere_mich_darum"]
        self.assertEqual(item["successful_uses"], 1)
        self.assertEqual(item["mastery"], 1)

    def test_ascii_alias_is_recognized(self):
        state = create_empty_state()
        result = handle_personal_sentence(
            "ich bringe ihnen sofort frische handtuecher",
            state,
            mode="course",
        )
        self.assertEqual(
            result["item"]["id"],
            "ich_bringe_ihnen_sofort_frische_handtuecher",
        )

    def test_progress_survives_state_completion(self):
        state = create_empty_state()
        handle_personal_sentence("Ich bin gleich fertig.", state)
        restored = complete_state(dict(state))
        memory = ensure_personal_sentence_memory(restored)
        self.assertEqual(
            memory["items"]["ich_bin_gleich_fertig"]["mastery"],
            1,
        )


if __name__ == "__main__":
    unittest.main()
