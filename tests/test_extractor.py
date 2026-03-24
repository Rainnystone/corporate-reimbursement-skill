import unittest
import os
from engine.extractor import extract_pdf_text

class TestExtractor(unittest.TestCase):
    def test_docling_extraction(self):
        # We will use one of the sample PDFs for testing
        test_pdf = os.path.join("sample set", "sample 2 202510", "input", "1010.pdf")

        # Ensure the file exists before testing
        if not os.path.exists(test_pdf):
            self.skipTest(f"Test file {test_pdf} not found.")

        text = extract_pdf_text(test_pdf)
        self.assertIsInstance(text, str)
        self.assertTrue(len(text) > 0)
        # Basic quality guard: extracted text should include key invoice/travel tokens.
        self.assertTrue(any(token in text for token in ["发票", "行程", "金额", "抬头", "公司"]))

if __name__ == '__main__':
    unittest.main()
