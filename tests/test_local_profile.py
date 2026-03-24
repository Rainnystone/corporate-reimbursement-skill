import tempfile
import unittest
import os
from pathlib import Path


class TestLocalProfile(unittest.TestCase):
    def test_load_returns_none_when_missing(self):
        from engine.local_profile import load_user_profile

        with tempfile.TemporaryDirectory() as tmp:
            profile = load_user_profile(base_dir=Path(tmp), user_name="alice")
            self.assertIsNone(profile)

    def test_save_and_load_profile(self):
        from engine.local_profile import load_user_profile, save_user_profile

        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            payload = {
                "base_company": "深圳市示例科技有限公司",
                "company_keywords": ["深圳示例", "示例科技"],
                "default_work_meal_headcount": 2,
                "max_work_meal_headcount": 6,
                "extra_review_items": ["检查餐费人数"],
            }
            save_user_profile(payload, base_dir=base, user_name="alice")
            loaded = load_user_profile(base_dir=base, user_name="alice")
            self.assertEqual(loaded["base_company"], payload["base_company"])
            self.assertEqual(loaded["default_work_meal_headcount"], 2)
            self.assertEqual(loaded["extra_review_items"], ["检查餐费人数"])

    def test_user_profiles_are_isolated(self):
        from engine.local_profile import load_user_profile, save_user_profile

        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            save_user_profile({"base_company": "A"}, base_dir=base, user_name="alice")
            save_user_profile({"base_company": "B"}, base_dir=base, user_name="bob")
            self.assertEqual(load_user_profile(base_dir=base, user_name="alice")["base_company"], "A")
            self.assertEqual(load_user_profile(base_dir=base, user_name="bob")["base_company"], "B")

    def test_env_override_path(self):
        from engine.local_profile import get_profile_path

        with tempfile.TemporaryDirectory() as tmp:
            old = os.environ.get("REIMBURSE_HOME")
            os.environ["REIMBURSE_HOME"] = tmp
            try:
                path = get_profile_path(user_name="alice")
                self.assertTrue(str(path).startswith(tmp))
            finally:
                if old is None:
                    os.environ.pop("REIMBURSE_HOME", None)
                else:
                    os.environ["REIMBURSE_HOME"] = old


if __name__ == "__main__":
    unittest.main()
