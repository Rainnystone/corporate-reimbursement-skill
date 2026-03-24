import unittest

class TestConfig(unittest.TestCase):
    def test_config_constants(self):
        from engine.config import HEADERS, EXCEL_MAPPING
        self.assertIsInstance(HEADERS, dict)
        self.assertIn("国内差旅详单", EXCEL_MAPPING["sheets"])

if __name__ == '__main__':
    unittest.main()
