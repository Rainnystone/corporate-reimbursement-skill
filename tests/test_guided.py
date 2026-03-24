import unittest


class TestGuidedHelpers(unittest.TestCase):
    def test_parse_headcount_response(self):
        from engine.guided import parse_headcount_response

        self.assertEqual(parse_headcount_response("2,3、2， 4"), [2, 3, 2, 4])
        self.assertEqual(parse_headcount_response(""), [])
        self.assertEqual(parse_headcount_response("x,3"), [3])

    def test_match_headcounts_exact(self):
        from engine.guided import apply_headcount_updates

        meals = [
            {"amount": 120.0, "headcount": 2},
            {"amount": 210.0, "headcount": 2},
            {"amount": 89.0, "headcount": 2},
        ]
        updated, mismatch, note = apply_headcount_updates(meals, [3, 2, 1], 2)
        self.assertFalse(mismatch)
        self.assertEqual([m["headcount"] for m in updated], [3, 2, 1])
        self.assertEqual(note, "")

    def test_match_headcounts_with_amount_fallback(self):
        from engine.guided import apply_headcount_updates

        meals = [
            {"amount": 95.0, "headcount": 2, "id": "a"},
            {"amount": 260.0, "headcount": 2, "id": "b"},
            {"amount": 180.0, "headcount": 2, "id": "c"},
        ]
        updated, mismatch, note = apply_headcount_updates(meals, [3, 1], 2)
        self.assertTrue(mismatch)
        # Highest amount should receive larger headcount first.
        by_id = {m["id"]: m["headcount"] for m in updated}
        self.assertEqual(by_id["b"], 3)
        self.assertEqual(by_id["c"], 1)
        self.assertEqual(by_id["a"], 2)
        self.assertIn("数量不一致", note)


if __name__ == "__main__":
    unittest.main()
