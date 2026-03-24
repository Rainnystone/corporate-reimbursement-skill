import re
import unicodedata
from collections import defaultdict
from typing import Dict, List, Tuple


COMPANY_KEYWORDS = (
    "有限公司",
    "有限责任公司",
    "集团",
    "股份",
    "公司",
    "事务所",
    "合伙",
    "基金",
    "科技",
    "咨询",
    "贸易",
    "投资",
)

STRICT_COMPANY_TOKENS = (
    "有限公司",
    "有限责任公司",
    "公司",
    "集团",
    "事务所",
    "合伙企业",
)

COMPANY_NOISE_WORDS = (
    "项目",
    "税率",
    "单价",
    "金额",
    "合计",
    "规格",
    "数量",
    "价税",
    "税额",
    "发票",
    "开票",
    "运输服务",
    "餐饮服务",
)

COMPANY_PREFIX_NOISE = (
    "名称",
    "备注",
    "购买方信息",
    "购方信息",
    "购买方名称",
    "购买方",
    "销售方信息",
    "销方",
    "单位名称",
    "公司名称",
    "统一社会信用代码纳税人识别号",
)

BUYER_CONTEXT_HINTS = ("购买方", "购方", "抬头", "单位名称", "公司名称")
SELLER_CONTEXT_HINTS = ("销售方", "销方")


def _clean_text(value: str) -> str:
    text = (value or "").strip()
    text = re.sub(r"\s+", " ", text)
    return text


def normalize_company_name(name: str) -> str:
    text = unicodedata.normalize("NFKC", _clean_text(name))
    text = re.sub(r"[（(].*?[)）]", "", text)  # remove parenthetical suffixes
    text = re.sub(r"[|｜:：/\\]+", "", text)
    text = text.replace(" ", "")
    return text[:80]


def _strip_noise_prefixes(text: str) -> str:
    value = text
    value = re.sub(r"^[0-9A-Za-z]+", "", value)
    changed = True
    while changed and value:
        changed = False
        for prefix in COMPANY_PREFIX_NOISE:
            if value.startswith(prefix):
                value = value[len(prefix) :]
                changed = True
    return value


def _extract_entity_like_chunks(text: str) -> List[str]:
    compact = normalize_company_name(text)
    pattern = (
        r"([一-龥A-Za-z0-9（）()·]{4,60}?"
        r"(?:有限责任公司|有限公司|合伙企业|事务所|集团|公司))"
    )
    return re.findall(pattern, compact)


def _is_valid_company_candidate(text: str) -> bool:
    if not text:
        return False
    if len(text) < 4 or len(text) > 50:
        return False
    if not any(token in text for token in STRICT_COMPANY_TOKENS):
        return False
    if any(word in text for word in COMPANY_NOISE_WORDS):
        return False
    if re.search(r"[^一-龥A-Za-z0-9（）()·]", text):
        return False
    return True


def looks_like_company(name: str) -> bool:
    text = normalize_company_name(name)
    if _is_valid_company_candidate(text):
        return True
    # Fallback for anonymized placeholders
    return "CORPORATE_ENTITY" in text or "ENTITY_" in text


def _extract_from_table(text: str) -> List[str]:
    candidates: List[str] = []
    compact = re.sub(r"\s+", "", text or "")
    buyer_patterns = [
        r"购买方信息.*?名称[:：]([^|]{4,120}?(?:有限责任公司|有限公司|合伙企业|事务所|集团|公司))",
        r"购买方名称[:：]([^|]{4,120}?(?:有限责任公司|有限公司|合伙企业|事务所|集团|公司))",
    ]
    for pattern in buyer_patterns:
        match = re.search(pattern, compact)
        if match:
            value = match.group(1)
            value = value.split("统一社会信用代码")[0]
            value = value.split("纳税人识别号")[0]
            value = _clean_text(value)
            if value:
                candidates.append(value)

    patterns = [
        r"\|\s*(?:购买方名称|购方名称|购买方|抬头|单位名称|公司名称)\s*\|\s*([^|]+?)\s*\|",
        r"(?:购买方名称|购方名称|购买方|抬头|单位名称|公司名称)[：:\s]+([^\n|]{4,80})",
    ]
    for pattern in patterns:
        for match in re.findall(pattern, text):
            cleaned = _clean_text(match)
            if cleaned:
                candidates.append(cleaned)
    return candidates


def _extract_from_lines(text: str) -> List[str]:
    candidates: List[str] = []
    for line in text.splitlines():
        line = _clean_text(line)
        if not line or len(line) > 80:
            continue
        if not any(k in line for k in STRICT_COMPANY_TOKENS):
            continue
        if not any(h in line for h in BUYER_CONTEXT_HINTS):
            continue
        if any(h in line for h in SELLER_CONTEXT_HINTS) and not any(
            h in line for h in BUYER_CONTEXT_HINTS
        ):
            continue
        if any(word in line for word in COMPANY_NOISE_WORDS):
            continue
        candidates.append(line)
    return candidates


def extract_company_candidates(text: str) -> List[str]:
    raw = _extract_from_table(text) + _extract_from_lines(text)
    normalized: List[str] = []
    seen = set()
    for item in raw:
        chunks = _extract_entity_like_chunks(item) or [normalize_company_name(item)]
        for chunk in chunks:
            cleaned = _strip_noise_prefixes(normalize_company_name(chunk))
            if _is_valid_company_candidate(cleaned) and cleaned not in seen:
                normalized.append(cleaned)
                seen.add(cleaned)
    return normalized


def _is_contextually_plausible(text: str, candidate: str) -> bool:
    compact_text = normalize_company_name(text)
    compact_candidate = normalize_company_name(candidate)
    idx = compact_text.find(compact_candidate)
    if idx < 0:
        return True
    start = max(0, idx - 24)
    end = min(len(compact_text), idx + len(compact_candidate) + 24)
    window = compact_text[start:end]
    has_buyer = any(h in window for h in BUYER_CONTEXT_HINTS)
    has_seller = any(h in window for h in SELLER_CONTEXT_HINTS)
    if has_seller and not has_buyer:
        return False
    if has_buyer:
        return True
    if "备注" in window or any(word in window for word in COMPANY_NOISE_WORDS):
        return False
    return True


def match_entity_by_aliases(text: str, aliases: List[str]) -> str:
    if not text or not aliases:
        return ""
    compact = normalize_company_name(text)
    matched: List[str] = []
    for alias in aliases:
        name = normalize_company_name(alias)
        if not name:
            continue
        if name in compact:
            matched.append(alias.strip())
    if len(matched) == 1:
        return matched[0]
    return ""


def infer_entity_name(text: str) -> str:
    candidates = extract_company_candidates(text)
    for candidate in candidates:
        if looks_like_company(candidate) and _is_contextually_plausible(text, candidate):
            return candidate
    return "UNKNOWN_ENTITY"


def group_files_by_entity(file_text_pairs: List[Tuple[str, str]]) -> Dict[str, List[str]]:
    grouped: Dict[str, List[str]] = defaultdict(list)
    for path, text in file_text_pairs:
        entity = infer_entity_name(text)
        grouped[entity].append(path)

    return dict(grouped)


def _extract_field(text: str, field: str) -> str:
    patterns = [
        rf"\|\s*{re.escape(field)}\s*\|\s*([^|]+?)\s*\|",
        rf"{re.escape(field)}[：:\s]+([^\n]+)",
    ]
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return _clean_text(match.group(1))
    return ""


def _normalize_city(city: str) -> str:
    text = _clean_text(city)
    if not text:
        return ""
    token = re.split(r"[\s,，/、]+", text)[0]
    token = token.replace("市", "")
    return token[:10]


def summarize_reason(reason: str, max_chars: int = 10) -> str:
    text = _clean_text(reason)
    if not text:
        return ""
    first_clause = re.split(r"[；;。,.，\n]", text)[0]
    first_clause = re.sub(r"\s+", "", first_clause)
    if len(first_clause) <= max_chars:
        return first_clause
    return first_clause[:max_chars] + "…"


def extract_travel_application_info(text: str) -> Dict[str, str]:
    departure = _normalize_city(_extract_field(text, "出发城市"))
    destination = _normalize_city(_extract_field(text, "目的城市"))
    reason = summarize_reason(_extract_field(text, "出差事由"))
    return {
        "departure_city": departure,
        "destination_city": destination,
        "travel_reason": reason,
    }


def extract_city_hint(text: str) -> str:
    for field in ("城市", "出发城市", "目的城市"):
        value = _normalize_city(_extract_field(text, field))
        if value:
            return value

    city_match = re.search(r"([一-龥]{2,6})市", text or "")
    if city_match:
        return city_match.group(1)
    return ""


def build_flight_details(
    departure_city: str = "",
    destination_city: str = "",
    travel_reason: str = "",
) -> str:
    departure = _normalize_city(departure_city)
    destination = _normalize_city(destination_city)
    reason = summarize_reason(travel_reason)

    route = ""
    if departure and destination:
        route = f"{departure}-{destination}"
    elif departure:
        route = departure
    elif destination:
        route = destination

    if route and reason:
        return f"机票费（{route}：{reason}）"
    if route:
        return f"机票费（{route}出差）"
    if reason:
        return f"机票费（{reason}）"
    return "机票费"


def _normalize_date(token: str) -> str:
    text = _clean_text(token)
    text = text.replace("年", "-").replace("月", "-").replace("日", "")
    text = text.replace("/", "-").replace(".", "-")
    m = re.search(r"(20\d{2})-(\d{1,2})-(\d{1,2})", text)
    if not m:
        return ""
    y, mm, dd = m.groups()
    return f"{y}-{int(mm):02d}-{int(dd):02d}"


def extract_invoice_date_amount(text: str) -> Tuple[str, float]:
    date = ""
    amount = 0.0

    date_candidates = re.findall(r"20\d{2}[年\-/\.]\d{1,2}[月\-/\.]\d{1,2}日?", text)
    for token in date_candidates:
        normalized = _normalize_date(token)
        if normalized:
            date = normalized
            break

    amount_patterns = [
        r"(?:价税合计|合计|金额|小写)[^0-9]{0,6}([0-9]+(?:\.[0-9]{1,2})?)",
        r"([0-9]+(?:\.[0-9]{1,2})?)\s*元",
    ]
    amount_candidates: List[float] = []
    for pattern in amount_patterns:
        for found in re.findall(pattern, text):
            try:
                value = float(found)
            except ValueError:
                continue
            if 0 < value < 1000000:
                amount_candidates.append(value)
    if amount_candidates:
        amount = max(amount_candidates)
    return date, round(amount, 2)


def _keyword_match_score(entity: str, keywords: List[str]) -> float:
    normalized_entity = normalize_company_name(entity)
    best = 0.0
    for keyword in keywords:
        k = normalize_company_name(keyword)
        if not k:
            continue
        if k == normalized_entity:
            best = max(best, 2.0)
        elif k in normalized_entity or normalized_entity in k:
            best = max(best, 1.0)
    return best


def select_primary_entity(
    grouped_files: Dict[str, List[str]], preferred_keywords: List[str]
) -> str:
    if not grouped_files:
        return "UNKNOWN_ENTITY"
    if not preferred_keywords:
        return max(grouped_files.items(), key=lambda kv: len(kv[1]))[0]

    scored = []
    for entity, files in grouped_files.items():
        score = _keyword_match_score(entity, preferred_keywords)
        scored.append((score, len(files), entity))
    scored.sort(reverse=True)
    top_score, _, top_entity = scored[0]
    if top_score > 0:
        return top_entity
    return max(grouped_files.items(), key=lambda kv: len(kv[1]))[0]
