import unittest
from unittest.mock import MagicMock, patch


class ExtractResumeContactTests(unittest.TestCase):
    def test_extracts_email_phone_and_heuristic_name(self):
        from app import rag

        text = (
            "Resume\n"
            "Aman Kumar\n"
            "Email: aman@example.com\n"
            "Mobile +1 (234) 567-8901\n"
        )
        fake_llm = MagicMock()
        with patch.object(rag, "llm_client", fake_llm):
            out = rag.extract_resume_contact_json(text)
        fake_llm.invoke.assert_not_called()
        self.assertEqual(out["name"], "Aman Kumar")
        self.assertEqual(out["email"], "aman@example.com")
        self.assertEqual(out["phone"], "12345678901")

    def test_llm_fills_missing_fields(self):
        from app import rag

        text = "Some resume body with no clear header.\nEmail: x@y.com\n"
        mock_msg = MagicMock()
        mock_msg.content = '{"name": "Nora Singh", "phone": "na", "email": "x@y.com"}'
        fake_llm = MagicMock()
        fake_llm.invoke.return_value = mock_msg
        with patch.object(rag, "llm_client", fake_llm):
            out = rag.extract_resume_contact_json(text)
        self.assertEqual(out["email"], "x@y.com")
        self.assertEqual(out["name"], "Nora Singh")


if __name__ == "__main__":
    unittest.main()
