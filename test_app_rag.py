import unittest


class RagModuleTests(unittest.TestCase):
    def test_rag_module_exposes_ask_question(self):
        from app import rag

        self.assertTrue(
            hasattr(rag, "ask_question"),
            "app.rag should expose ask_question for the /ask endpoint",
        )


if __name__ == "__main__":
    unittest.main()
