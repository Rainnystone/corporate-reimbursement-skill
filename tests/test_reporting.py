import tempfile
import unittest
from pathlib import Path


class TestReporting(unittest.TestCase):
    def test_render_and_write_report(self):
        from engine.reporting import render_run_report, write_run_report

        report = {
            "user_name": "alice",
            "primary_entity": "深圳市示例科技有限公司",
            "work_meal_count": 2,
            "work_meal_total": 280.0,
            "work_meal_capped_total": 240.0,
            "output_files": ["/tmp/a.xlsx"],
            "review_items": ["工作餐人数", "机票行程摘要"],
            "notes": ["有 1 条人数使用了临时匹配"],
        }
        text = render_run_report(report)
        self.assertIn("深圳市示例科技有限公司", text)
        self.assertIn("工作餐人数", text)
        self.assertIn("/tmp/a.xlsx", text)

        with tempfile.TemporaryDirectory() as tmp:
            path = write_run_report(report, Path(tmp))
            self.assertTrue(path.exists())
            loaded = path.read_text(encoding="utf-8")
            self.assertIn("机票行程摘要", loaded)


if __name__ == "__main__":
    unittest.main()
