import json
import argparse
from datetime import datetime
from engine.excel_engine import ReimbursementExcel, safe_write
from engine.semantic import build_flight_details, extract_travel_application_info

def format_date_str(date_str):
    if not date_str: return ""
    dt = datetime.strptime(date_str, "%Y-%m-%d")
    return f"{dt.year}年{dt.month}月"

def unmerge_at_cell(worksheet, coordinate):
    for merged_range in list(worksheet.merged_cells.ranges):
        if coordinate in merged_range:
            worksheet.unmerge_cells(str(merged_range))
            break

def clean_city(city):
    if not city: return ""
    text = str(city).strip()
    if text.endswith("市"):
        text = text[:-1]
    return text

def find_anchor_row(worksheet, search_val, start_row=1, col_idx=2):
    for r in range(start_row, 100):
        v = worksheet.cell(row=r, column=col_idx).value
        if v and search_val in str(v):
            return r
    return None

def populate_excel(data, template_path, output_path, header_type):
    excel = ReimbursementExcel(template_path)
    ws_travel = excel.workbook["国内差旅详单"]
    
    # 1. Hotel
    row = 5
    for item in data.get("hotel", []):
        safe_write(ws_travel, f"B{row}", format_date_str(item["date"]))
        safe_write(ws_travel, f"C{row}", clean_city(item["city"]))
        safe_write(ws_travel, f"D{row}", "住宿")
        safe_write(ws_travel, f"F{row}", "RMB")
        safe_write(ws_travel, f"G{row}", item["amount"])
        safe_write(ws_travel, f"I{row}", 1)
        row += 1

    # 2. Dining
    dining_anchor = find_anchor_row(ws_travel, "餐费", 1, 2)
    if dining_anchor:
        row = dining_anchor + 2
        grouped_dining = {}
        for item in data.get("dining", []):
            key = (format_date_str(item["date"]), clean_city(item["city"]), item["category"])
            if key not in grouped_dining:
                grouped_dining[key] = {"amount": 0, "count": 0}
            grouped_dining[key]["amount"] += item["amount"]
            grouped_dining[key]["count"] += 1
        for (date_str, city, cat), vals in sorted(grouped_dining.items()):
            unmerge_at_cell(ws_travel, f"B{row}")
            summary = "工作餐" if "工作餐" in cat else "招待"
            safe_write(ws_travel, f"B{row}", date_str)
            safe_write(ws_travel, f"C{row}", city)
            safe_write(ws_travel, f"D{row}", summary)
            safe_write(ws_travel, f"F{row}", "RMB")
            safe_write(ws_travel, f"G{row}", vals["amount"])
            safe_write(ws_travel, f"I{row}", vals["count"])
            row += 1

    # 3. Others
    other_anchor = find_anchor_row(ws_travel, "其它费用", 1, 2)
    if other_anchor:
        row = other_anchor + 2
        for item in data.get("phone", []):
            unmerge_at_cell(ws_travel, f"B{row}")
            safe_write(ws_travel, f"B{row}", format_date_str(item["date"]))
            safe_write(ws_travel, f"C{row}", clean_city(item["city"]))
            safe_write(ws_travel, f"D{row}", "话费")
            safe_write(ws_travel, f"F{row}", "RMB")
            safe_write(ws_travel, f"G{row}", item["amount"])
            safe_write(ws_travel, f"I{row}", 1)
            row += 1

    # 4. Didi (Detail 2)
    ws_trans2 = excel.workbook["国内交通详单（2）"]
    didi_anchor = find_anchor_row(ws_trans2, "三、增值税普通电子发票", 1, 2)
    if didi_anchor:
        row = didi_anchor 
        for item in data.get("transport", []):
            if "滴滴" in item["category"]:
                total = item["amount"]
                pre_tax = round(total / 1.03, 2)
                tax = round(total - pre_tax, 2)
                safe_write(ws_trans2, f"B{row}", None) 
                safe_write(ws_trans2, f"C{row}", format_date_str(item["date"]))
                safe_write(ws_trans2, f"D{row}", clean_city(item["city"]))
                safe_write(ws_trans2, f"E{row}", "滴滴费用")
                safe_write(ws_trans2, f"F{row}", "RMB")
                safe_write(ws_trans2, f"G{row}", pre_tax)
                safe_write(ws_trans2, f"H{row}", tax)
                safe_write(ws_trans2, f"K{row}", 1)
                row += 1

    # 5. Flight (Detail 1)
    ws_trans1 = excel.workbook["国内交通详单（1）"]
    flight_anchor = find_anchor_row(ws_trans1, "二、航空运输电子客票行程单", 1, 2)
    if flight_anchor:
        row = flight_anchor
        travel_context = data.get("travel_context", {})
        if not travel_context and data.get("travel_application_text"):
            travel_context = extract_travel_application_info(data["travel_application_text"])
        for item in data.get("transport", []):
            if "机票" in item["category"]:
                departure = item.get("departure_city") or travel_context.get("departure_city", "")
                destination = item.get("destination_city") or travel_context.get("destination_city", "")
                reason = item.get("travel_reason") or travel_context.get("travel_reason", "")
                details = item.get("details") or build_flight_details(departure, destination, reason)

                safe_write(ws_trans1, f"C{row}", format_date_str(item["date"]))
                safe_write(ws_trans1, f"D{row}", clean_city(departure or item.get("city", "")))
                safe_write(ws_trans1, f"E{row}", details)
                safe_write(ws_trans1, f"F{row}", "RMB")
                if "ticket" in item:
                    safe_write(ws_trans1, f"G{row}", item["ticket"])
                    safe_write(ws_trans1, f"H{row}", item["fund"])
                    safe_write(ws_trans1, f"I{row}", item["fuel"])
                else:
                    safe_write(ws_trans1, f"G{row}", item.get("amount", 0))
                    safe_write(ws_trans1, f"H{row}", 0)
                    safe_write(ws_trans1, f"I{row}", 0)
                safe_write(ws_trans1, f"M{row}", 1)
                row += 1

    # 6. Cover Page Summary
    ws_cover = excel.workbook["付款申请表（面单）"]
    
    # Determine the Period from available dates
    period_str = "Unknown"
    for cat in ["dining", "transport", "hotel", "phone"]:
        if data.get(cat):
            period_str = format_date_str(data[cat][0]["date"])
            break

    # Entity-agnostic summary
    cat_map = {
        "机票": sum(i["amount"] for i in data.get("transport", []) if "机票" in i["category"]),
        "交通：滴滴": sum(i["amount"] for i in data.get("transport", []) if "滴滴" in i["category"]),
        "酒店住宿": sum(i["amount"] for i in data.get("hotel", [])),
        "餐费": sum(i["amount"] for i in data.get("dining", [])),
        "其他费用：话费": sum(i["amount"] for i in data.get("phone", [])),
    }
    order = ["机票", "交通：滴滴", "酒店住宿", "餐费", "其他费用：话费"]

    # Fill Payee/Bank/Account if present in data
    if "payee" in data: safe_write(ws_cover, "D22", data["payee"])
    if "bank" in data: safe_write(ws_cover, "D23", data["bank"])
    if "account" in data: safe_write(ws_cover, "D24", data["account"])

    row = 9
    for name in order:
        amount = cat_map.get(name, 0)
        if amount > 0:
            safe_write(ws_cover, f"B{row}", name)
            safe_write(ws_cover, f"D{row}", period_str)
            safe_write(ws_cover, f"F{row}", amount)
            row += 1

    excel.save(output_path)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", required=True)
    parser.add_argument("--template", required=True)
    parser.add_argument("--header", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    with open(args.json, 'r') as f:
        all_data = json.load(f)
    populate_excel(all_data[args.header], args.template, args.output, args.header)
