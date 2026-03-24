import unittest

from reimburse import (
    build_entity_payload,
    build_work_meal_records,
    classify_pdf_category,
    parse_text_list,
    resolve_entity_for_execution,
)


class TestCliFlowHelpers(unittest.TestCase):
    def test_parse_text_list(self):
        self.assertEqual(parse_text_list("a,b、c，d"), ["a", "b", "c", "d"])
        self.assertEqual(parse_text_list(""), [])

    def test_classify_pdf_category(self):
        self.assertEqual(classify_pdf_category("/tmp/input/工作餐/a.pdf"), "work_meal")
        self.assertEqual(classify_pdf_category("/tmp/input/招待/b.pdf"), "hospitality")
        self.assertEqual(
            classify_pdf_category("/tmp/input/员工提交的出差申请202510211642000594585.pdf"),
            "travel_application",
        )

    def test_build_work_meal_records(self):
        file_records = [
            {"file": "1.pdf", "category": "work_meal", "date": "2025-11-02", "amount": 220.0},
            {"file": "2.pdf", "category": "hospitality", "date": "2025-11-03", "amount": 300.0},
            {"file": "3.pdf", "category": "work_meal", "date": "2025-11-01", "amount": 120.0},
        ]
        meals = build_work_meal_records(file_records, 2)
        self.assertEqual(len(meals), 2)
        self.assertEqual(meals[0]["date"], "2025-11-01")
        self.assertEqual(meals[1]["capped_amount"], 160.0)

    def test_build_entity_payload(self):
        records = [
            {
                "file": "wm.pdf",
                "category": "work_meal",
                "date": "2025-11-01",
                "city": "上海",
                "amount": 300.0,
            },
            {
                "file": "ft.pdf",
                "category": "flight_invoice",
                "date": "2025-11-02",
                "city": "城市甲",
                "amount": 1200.0,
            },
            {
                "file": "ta.pdf",
                "category": "travel_application",
                "text": "出发城市 城市甲 目的城市 城市乙",
            },
        ]
        corrected = {"wm.pdf": {"capped_amount": 160.0}}
        payload = build_entity_payload(records, corrected)
        self.assertEqual(payload["dining"][0]["amount"], 160.0)
        self.assertEqual(payload["transport"][0]["category"], "机票")
        self.assertIn("travel_application_text", payload)

    def test_resolve_entity_for_execution_no_unknown_output(self):
        profile = {
            "base_company": "示例主体A有限公司",
            "company_keywords": ["示例主体B有限公司"],
        }
        entity, fallback = resolve_entity_for_execution("UNKNOWN_ENTITY", "无明确抬头", profile)
        self.assertEqual(entity, "示例主体A有限公司")
        self.assertTrue(fallback)


if __name__ == "__main__":
    unittest.main()
