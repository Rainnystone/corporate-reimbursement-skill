import unittest
import os
from reimbursement.extractor import extract_pdf_text
from reimbursement.config import HEADERS

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
        # Check if it extracted one of the target headers (use placeholder for GitHub safety)
        self.assertTrue(any(h in text for h in HEADERS.values()) or "CORPORATE" in text)

if __name__ == '__main__':
    unittest.main()
