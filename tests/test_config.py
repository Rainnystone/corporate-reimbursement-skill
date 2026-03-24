import unittest

class TestConfig(unittest.TestCase):
    def test_config_constants(self):
        from reimbursement.config import HEADERS, EXCEL_MAPPING
        self.assertIn("BJ", HEADERS)
        self.assertIn("SH", HEADERS)
        self.assertIn("国内差旅详单", EXCEL_MAPPING["sheets"])

if __name__ == '__main__':
    unittest.main()
