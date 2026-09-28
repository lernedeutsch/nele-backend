import unittest
from unittest.mock import patch

from brain.logic.knowledge_retriever import KnowledgeItem, retrieve


class KnowledgeRetrieverTests(unittest.TestCase):
    def test_returns_common_knowledge_item_shape(self):
        items = retrieve(topic="Hobbys", level="A1", sources=("dialogue",), limit=3)
        self.assertTrue(items)
        self.assertTrue(all(isinstance(item, KnowledgeItem) for item in items))
        self.assertTrue(all(item.source == "dialogue" for item in items))
        self.assertIn("hobby", items[0].topic.lower())

    def test_meine_saetze_can_be_retrieved_by_topic(self):
        items = retrieve(topic="hotel", level="A1", sources=("meine_saetze",), limit=5)
        self.assertTrue(items)
        self.assertEqual(items[0].source, "meine_saetze")
        self.assertEqual(items[0].topic, "hotel")

    @patch("brain.logic.knowledge_retriever.load_lesson")
    def test_lesson_adapter_normalizes_existing_content(self, load_lesson):
        load_lesson.return_value = [{"text": "Ich komme aus Polen.", "topic": "Herkunft", "tags": ["kommen"]}]
        items = retrieve(query="Polen", topic="Herkunft", level="A1", lesson=2, sources=("lesson",))
        self.assertEqual(items[0].text, "Ich komme aus Polen.")
        self.assertEqual(items[0].source, "lesson")
        self.assertGreater(items[0].score, 0)

    @patch("brain.logic.knowledge_retriever.ACTIVE_DIALOGUES", [])
    @patch("brain.logic.knowledge_retriever.PERSONAL_SENTENCES", [])
    @patch("brain.logic.knowledge_retriever.load_lesson", return_value=[])
    def test_empty_sources_return_controlled_empty_list(self, _load):
        self.assertEqual(retrieve(query="unknown", lesson=99), [])


if __name__ == "__main__":
    unittest.main()
