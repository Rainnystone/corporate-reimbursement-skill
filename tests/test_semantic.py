import unittest

from engine.semantic import (
    extract_city_hint,
    extract_invoice_date_amount,
    build_flight_details,
    extract_travel_application_info,
    group_files_by_entity,
    infer_entity_name,
    match_entity_by_aliases,
    normalize_company_name,
    select_primary_entity,
)


class TestSemantic(unittest.TestCase):
    def test_infer_entity_name_from_invoice_text(self):
        text = """
        | 购买方名称 | 深圳市示例科技有限公司 |
        | 价税合计 | 123.00 |
        """
        entity = infer_entity_name(text)
        self.assertEqual(entity, "深圳市示例科技有限公司")

    def test_group_unknown_into_dominant_entity(self):
        grouped = group_files_by_entity(
            [
                ("a.pdf", "| 购买方名称 | 上海某某投资管理有限公司 |"),
                ("b.pdf", "内容缺失"),
                ("c.pdf", "| 购买方名称 | 上海某某投资管理有限公司 |"),
            ]
        )
        self.assertIn("上海某某投资管理有限公司", grouped)
        self.assertEqual(len(grouped["上海某某投资管理有限公司"]), 2)
        self.assertIn("UNKNOWN_ENTITY", grouped)
        self.assertEqual(grouped["UNKNOWN_ENTITY"], ["b.pdf"])

    def test_extract_travel_info_and_build_details(self):
        text = """
        | 出差事由 | 客户拜访 |
        | 出发城市 | 南京市 |
        | 目的城市 | 苏州市 |
        """
        info = extract_travel_application_info(text)
        self.assertEqual(info["departure_city"], "南京")
        self.assertEqual(info["destination_city"], "苏州")
        self.assertTrue(info["travel_reason"].startswith("客户拜访"))

        details = build_flight_details(
            info["departure_city"], info["destination_city"], info["travel_reason"]
        )
        self.assertIn("南京-苏州", details)
        self.assertIn("机票费", details)

    def test_select_primary_entity_with_keyword(self):
        grouped = {
            "上海某某投资管理有限公司": ["a.pdf", "b.pdf"],
            "深圳市示例科技有限公司": ["c.pdf"],
        }
        selected = select_primary_entity(grouped, ["深圳市示例科技有限公司"])
        self.assertEqual(selected, "深圳市示例科技有限公司")

    def test_extract_invoice_date_and_amount(self):
        text = """
        开票日期: 2025年11月12日
        价税合计(小写) ￥278.50
        """
        d, a = extract_invoice_date_amount(text)
        self.assertEqual(d, "2025-11-12")
        self.assertEqual(a, 278.50)

    def test_extract_city_hint(self):
        text = """
        | 城市 | 上海 |
        """
        self.assertEqual(extract_city_hint(text), "上海")

    def test_extract_buyer_from_purchase_info_block(self):
        text = """
        旅客运输服务
        购 买 方 信 息 名称： 示例主体B有限公司 统一社会信用代码/纳税人识别号：911...
        销 售 方 信 息 名称： 上海滴滴畅行科技有限公司
        """
        self.assertEqual(
            infer_entity_name(text),
            "示例主体B有限公司",
        )

    def test_infer_entity_name_ignores_department_line(self):
        text = "| 创建人部门 | 投资/前台 |"
        self.assertEqual(infer_entity_name(text), "UNKNOWN_ENTITY")

    def test_normalize_company_name_unifies_compatibility_chars(self):
        self.assertEqual(
            normalize_company_name("示例主体A有限公司"),
            normalize_company_name("示例主体A有限公司"),
        )

    def test_match_entity_by_aliases_exact(self):
        text = "购买方信息 名称：示例主体B有限公司 统一社会信用代码..."
        aliases = ["示例主体A有限公司", "示例主体B有限公司"]
        self.assertEqual(
            match_entity_by_aliases(text, aliases),
            "示例主体B有限公司",
        )


if __name__ == "__main__":
    unittest.main()
