import re
from typing import Dict, List, Tuple


def parse_headcount_response(text: str) -> List[int]:
    if not text or not text.strip():
        return []
    parts = re.split(r"[,\s、，;；]+", text.strip())
    values: List[int] = []
    for part in parts:
        if part.isdigit():
            values.append(int(part))
    return values


def _recalc_meal(meal: Dict, default_headcount: int) -> Dict:
    item = dict(meal)
    headcount = item.get("headcount", default_headcount) or default_headcount
    amount = float(item.get("amount", 0) or 0)
    item["headcount"] = int(headcount)
    item["capped_amount"] = round(min(amount, item["headcount"] * 80), 2)
    return item


def apply_headcount_updates(
    meals: List[Dict], counts: List[int], default_headcount: int
) -> Tuple[List[Dict], bool, str]:
    items = [_recalc_meal(m, default_headcount) for m in meals]
    if not counts:
        return items, False, ""

    if len(counts) == len(items):
        updated: List[Dict] = []
        for item, count in zip(items, counts):
            item["headcount"] = count
            item["capped_amount"] = round(min(float(item.get("amount", 0) or 0), count * 80), 2)
            updated.append(item)
        return updated, False, ""

    # fallback: sort by amount desc and assign larger headcounts to larger amounts
    sorted_idx = sorted(range(len(items)), key=lambda i: float(items[i].get("amount", 0) or 0), reverse=True)
    sorted_counts = sorted(counts, reverse=True)
    for pos, idx in enumerate(sorted_idx):
        if pos < len(sorted_counts):
            c = sorted_counts[pos]
            items[idx]["headcount"] = c
            items[idx]["capped_amount"] = round(
                min(float(items[idx].get("amount", 0) or 0), c * 80), 2
            )
    note = "人数数量不一致，已按金额大小做临时匹配，请确认或补全完整人数列表。"
    return items, True, note

