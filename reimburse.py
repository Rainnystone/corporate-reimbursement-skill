#!/usr/bin/env python3
import argparse
import os
import glob
from pathlib import Path
from typing import Dict, List, Tuple

from engine.guided import apply_headcount_updates, parse_headcount_response
from engine.local_profile import get_profile_path, load_user_profile, save_user_profile
from engine.populate import populate_excel
from engine.reporting import render_run_report, write_run_report
from engine.semantic import (
    extract_city_hint,
    extract_invoice_date_amount,
    extract_travel_application_info,
    infer_entity_name,
    match_entity_by_aliases,
    normalize_company_name,
    select_primary_entity,
)
from engine.utils import setup_logger
from engine.extractor import extract_pdf_text

logger = setup_logger("reimbursement_engine")


def parse_text_list(text: str) -> List[str]:
    if not text:
        return []
    items = []
    for token in text.replace("、", ",").replace("，", ",").split(","):
        value = token.strip()
        if value:
            items.append(value)
    return items


def ask_text(prompt: str, default: str = "") -> str:
    value = input(prompt).strip()
    return value or default


def ask_int(prompt: str, default: int) -> int:
    value = input(prompt).strip()
    if not value:
        return default
    if value.isdigit() and int(value) > 0:
        return int(value)
    print(f"输入无效，使用默认值 {default}")
    return default


def classify_pdf_category(pdf_path: str) -> str:
    path = Path(pdf_path)
    name = path.name
    parts = set(path.parts)

    if "工作餐" in parts:
        return "work_meal"
    if "招待" in parts:
        return "hospitality"
    if "出差" in name and "提交" in name:
        return "travel_application"
    if "机票" in name or "客票" in name:
        return "flight_invoice"
    if "滴滴" in name:
        return "didi"
    if "话费" in name:
        return "phone"
    if any(k in name for k in ("酒店", "亚朵", "住宿")):
        return "hotel"
    return "other"


def setup_profile(existing: Dict) -> Dict:
    print("\n首次/重设引导：本配置仅保存在本机，不会写入仓库。", flush=True)
    print("使用前请先整理材料：所有发票放在同一个 input 文件夹；餐饮需放在 input/工作餐 和 input/招待。", flush=True)
    base_company_default = existing.get("base_company", "")
    base_company = ask_text("1) 请输入默认报销主体全名（精确）: ", base_company_default)

    keyword_default = ",".join(existing.get("company_keywords", []))
    keyword_text = ask_text(
        "2) 可选：补充其它并行主体全名（精确，逗号分隔）: ",
        keyword_default,
    )
    company_keywords = parse_text_list(keyword_text)
    if base_company and base_company not in company_keywords:
        company_keywords = [base_company] + company_keywords

    default_headcount = ask_int(
        "3) 工作餐默认人数（直接回车默认 2）: ",
        int(existing.get("default_work_meal_headcount", 2) or 2),
    )
    max_headcount = ask_int(
        "4) 工作餐常见最大人数（直接回车默认 6）: ",
        int(existing.get("max_work_meal_headcount", 6) or 6),
    )

    print(
        "5) 餐饮分类规则已切换为文件夹方式：请把文件放到 input/工作餐 和 input/招待",
        flush=True,
    )
    return {
        "base_company": base_company,
        "company_keywords": company_keywords,
        "default_work_meal_headcount": default_headcount,
        "max_work_meal_headcount": max_headcount,
        "extra_review_items": existing.get("extra_review_items", []),
    }


def build_work_meal_records(
    file_records: List[Dict], default_headcount: int
) -> List[Dict]:
    records: List[Dict] = []
    for item in file_records:
        if item["category"] != "work_meal":
            continue
        amount = float(item.get("amount", 0) or 0)
        headcount = int(item.get("headcount", default_headcount) or default_headcount)
        records.append(
            {
                "file": item["file"],
                "date": item.get("date", ""),
                "amount": amount,
                "headcount": headcount,
                "capped_amount": round(min(amount, headcount * 80), 2),
            }
        )
    records.sort(key=lambda x: (x.get("date", ""), x.get("amount", 0)))
    return records


def print_work_meal_records(records: List[Dict]) -> None:
    if not records:
        print("\n工作餐目录未发现可处理记录。")
        return
    print("\n工作餐人数清单（请按顺序回复人数，如 2,3,2...）:")
    for idx, item in enumerate(records, start=1):
        print(
            f"{idx}. 日期 {item.get('date') or '未知'} | 金额 {item['amount']:.2f} | "
            f"当前人数 {item['headcount']} | 封顶后 {item['capped_amount']:.2f}"
        )


def update_work_meal_headcounts_interactive(
    records: List[Dict], default_headcount: int
) -> Tuple[List[Dict], List[str]]:
    notes: List[str] = []
    if not records:
        return records, notes

    print_work_meal_records(records)
    raw = input("请输入人数列表（逗号或顿号分隔，回车则保持默认）: ").strip()
    if not raw:
        notes.append("未提供人数修正，已保留默认人数。")
        return records, notes

    counts = parse_headcount_response(raw)
    updated, mismatch, note = apply_headcount_updates(records, counts, default_headcount)
    if not mismatch:
        notes.append("已按你提供的人数重新计算工作餐。")
        return updated, notes

    notes.append(note)
    print(note)
    print_work_meal_records(updated)
    confirm = input("输入 Y 确认临时匹配，或输入完整人数列表重新计算: ").strip()
    if confirm.lower() == "y":
        notes.append("你已确认临时匹配结果。")
        return updated, notes

    second = parse_headcount_response(confirm)
    if len(second) == len(records):
        corrected, _, _ = apply_headcount_updates(records, second, default_headcount)
        notes.append("已按补全后的人数列表重新计算。")
        return corrected, notes

    notes.append("补充人数仍不完整，沿用临时匹配结果。")
    return updated, notes


def sanitize_entity_for_filename(entity: str) -> str:
    text = (entity or "UNKNOWN_ENTITY").strip()
    safe = "".join(ch if ch.isalnum() else "_" for ch in text)
    return safe[:60] or "UNKNOWN_ENTITY"


def build_entity_payload(
    records: List[Dict],
    corrected_work_meals: Dict[str, Dict],
) -> Dict:
    payload = {
        "hotel": [],
        "dining": [],
        "transport": [],
        "phone": [],
    }

    travel_text = ""
    for rec in records:
        category = rec.get("category")
        if category == "work_meal":
            corrected = corrected_work_meals.get(rec["file"])
            amount = corrected["capped_amount"] if corrected else rec.get("amount", 0)
            payload["dining"].append(
                {
                    "date": rec.get("date", ""),
                    "city": rec.get("city", ""),
                    "category": "工作餐",
                    "amount": round(float(amount or 0), 2),
                }
            )
            continue

        if category == "hospitality":
            payload["dining"].append(
                {
                    "date": rec.get("date", ""),
                    "city": rec.get("city", ""),
                    "category": "招待",
                    "amount": round(float(rec.get("amount", 0) or 0), 2),
                }
            )
            continue

        if category == "hotel":
            payload["hotel"].append(
                {
                    "date": rec.get("date", ""),
                    "city": rec.get("city", ""),
                    "amount": round(float(rec.get("amount", 0) or 0), 2),
                }
            )
            continue

        if category == "phone":
            payload["phone"].append(
                {
                    "date": rec.get("date", ""),
                    "city": rec.get("city", ""),
                    "amount": round(float(rec.get("amount", 0) or 0), 2),
                }
            )
            continue

        if category == "didi":
            payload["transport"].append(
                {
                    "date": rec.get("date", ""),
                    "city": rec.get("city", ""),
                    "category": "滴滴",
                    "amount": round(float(rec.get("amount", 0) or 0), 2),
                }
            )
            continue

        if category == "flight_invoice":
            payload["transport"].append(
                {
                    "date": rec.get("date", ""),
                    "city": rec.get("city", ""),
                    "category": "机票",
                    "amount": round(float(rec.get("amount", 0) or 0), 2),
                }
            )
            continue

        if category == "travel_application":
            travel_text = rec.get("text", "")

    if travel_text:
        payload["travel_application_text"] = travel_text
    return payload


def resolve_entity_for_execution(
    raw_entity: str,
    text: str,
    profile: Dict,
) -> Tuple[str, bool]:
    aliases = [profile.get("base_company", "")] + profile.get("company_keywords", [])
    aliases = [a.strip() for a in aliases if a and a.strip()]
    if aliases:
        canonical = {normalize_company_name(a): a for a in aliases}
        norm_raw = normalize_company_name(raw_entity)
        if norm_raw in canonical:
            return canonical[norm_raw], False

        alias_match = match_entity_by_aliases(text, aliases)
        if alias_match:
            return alias_match, False

        default_entity = profile.get("base_company", "").strip() or aliases[0]
        return default_entity, True

    if raw_entity and raw_entity != "UNKNOWN_ENTITY":
        return raw_entity, False
    return "DEFAULT_ENTITY", True


def process_directory(input_dir, template_path, output_dir, profile, interactive=True):
    logger.info(f"Starting reimbursement processing...")
    logger.info(f"Input: {input_dir}")
    logger.info(f"Template: {template_path}")
    logger.info(f"Output: {output_dir}")

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # 1. Find all PDFs
    pdf_files = glob.glob(os.path.join(input_dir, "**/*.pdf"), recursive=True)
    logger.info(f"Found {len(pdf_files)} PDF files.")

    # 2. Extract text and group by inferred corporate entity
    file_records: List[Dict] = []
    for pdf in pdf_files:
        text = extract_pdf_text(pdf)
        category = classify_pdf_category(pdf)
        date, amount = extract_invoice_date_amount(text)
        raw_entity = infer_entity_name(text)
        entity, fallback_used = resolve_entity_for_execution(raw_entity, text, profile)
        file_records.append(
            {
                "file": pdf,
                "text": text,
                "entity": entity,
                "raw_entity": raw_entity,
                "entity_fallback_used": fallback_used,
                "category": category,
                "date": date,
                "amount": amount,
                "city": extract_city_hint(text),
            }
        )

    grouped: Dict[str, List[str]] = {}
    for rec in file_records:
        grouped.setdefault(rec["entity"], []).append(rec["file"])
    preferred_keywords = [profile.get("base_company", "")] + profile.get("company_keywords", [])
    primary_entity = select_primary_entity(grouped, preferred_keywords)
    reverse_lookup = {
        path: entity for entity, files in grouped.items() for path in files
    }

    entity_records: Dict[str, List[Dict]] = {}
    for rec in file_records:
        rec["entity"] = reverse_lookup.get(rec["file"], rec["entity"])
        logger.info(f"Processed {rec['file']} -> Entity: {rec['entity']}")
        entity_records.setdefault(rec["entity"], []).append(rec)

    default_headcount = int(profile.get("default_work_meal_headcount", 2) or 2)
    max_headcount = int(profile.get("max_work_meal_headcount", 6) or 6)
    primary_records = entity_records.get(primary_entity, file_records)
    work_meal_records = build_work_meal_records(primary_records, default_headcount)
    notes: List[str] = []
    if interactive:
        work_meal_records, headcount_notes = update_work_meal_headcounts_interactive(
            work_meal_records, default_headcount
        )
        notes.extend(headcount_notes)
    corrected_work_meals = {item["file"]: item for item in work_meal_records}

    if any(item["headcount"] > max_headcount for item in work_meal_records):
        notes.append(f"发现超过常见人数上限（{max_headcount}）的工作餐记录，请人工复核。")

    fallback_count = sum(1 for rec in file_records if rec.get("entity_fallback_used"))
    if fallback_count:
        notes.append(f"有 {fallback_count} 份票据主体使用了兜底归属，请重点复核主体拆分。")

    travel_context = {}
    for record in primary_records:
        if record["category"] == "travel_application":
            travel_context = extract_travel_application_info(record["text"])
            break
    if travel_context:
        notes.append(
            "已提取出差行程："
            f"{travel_context.get('departure_city', '')}-"
            f"{travel_context.get('destination_city', '')}，请复核机票摘要。"
        )

    unclassified_count = sum(1 for rec in file_records if rec.get("category") == "other")
    if unclassified_count:
        notes.append(f"有 {unclassified_count} 份文件未进入已支持分类，请人工检查。")

    output_files: List[str] = []
    if not entity_records:
        notes.append("未检测到可处理发票文件。")
    for entity, records in entity_records.items():
        logger.info(f"Generating Excel for entity: {entity} ({len(records)} files)")
        payload = build_entity_payload(records, corrected_work_meals)
        safe_entity = sanitize_entity_for_filename(entity)
        output_file = os.path.join(output_dir, f"Reimbursement_{safe_entity}.xlsx")
        try:
            populate_excel(payload, template_path, output_file, entity)
            output_files.append(output_file)
        except Exception as exc:
            notes.append(f"{entity} 生成失败: {exc}")

    work_meal_total = round(sum(item.get("amount", 0) for item in work_meal_records), 2)
    work_meal_capped_total = round(sum(item.get("capped_amount", 0) for item in work_meal_records), 2)
    review_items = ["工作餐人数", "机票行程摘要", "报销主体识别"]
    review_items.extend(profile.get("extra_review_items", []))
    review_items = list(dict.fromkeys([i for i in review_items if i]))

    report = {
        "user_name": os.environ.get("USER", ""),
        "primary_entity": primary_entity,
        "work_meal_count": len(work_meal_records),
        "work_meal_total": work_meal_total,
        "work_meal_capped_total": work_meal_capped_total,
        "output_files": output_files,
        "review_items": review_items,
        "notes": notes,
    }
    report_path = write_run_report(report, Path(output_dir))
    print("\n" + render_run_report(report))
    print(f"报告已保存到: {report_path}")

    logger.info("Processing complete.")
    return report, report_path


def capture_first_run_review_items(profile: Dict) -> Dict:
    text = input(
        "首次运行完成。你希望后续每次固定加哪些复核项？可用逗号分隔，留空跳过: "
    ).strip()
    items = parse_text_list(text)
    if items:
        profile["extra_review_items"] = items
    return profile

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Corporate Reimbursement Automation Engine")
    parser.add_argument("--input-dir", required=True, help="Directory containing input invoices (PDFs/Images)")
    parser.add_argument("--template", required=True, help="Path to the blank Excel template")
    parser.add_argument("--output-dir", required=True, help="Directory to save generated Excel files")
    parser.add_argument("--setup", action="store_true", help="Force guided setup and overwrite local profile")

    args = parser.parse_args()
    profile = load_user_profile()
    is_first_run = profile is None
    if is_first_run or args.setup:
        profile = setup_profile(profile or {})
        profile_path = save_user_profile(profile)
        print(f"本地配置已保存到: {profile_path}")
    else:
        profile_path = get_profile_path()
        print(f"已读取本地配置: {profile_path}")

    process_directory(args.input_dir, args.template, args.output_dir, profile, interactive=True)

    if is_first_run:
        profile = capture_first_run_review_items(profile)
        profile_path = save_user_profile(profile)
        print(f"已更新复核项到本地配置: {profile_path}")
