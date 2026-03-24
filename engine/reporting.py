from datetime import datetime
from pathlib import Path
from typing import Dict, List


def render_run_report(report: Dict) -> str:
    review_items: List[str] = report.get("review_items", [])
    notes: List[str] = report.get("notes", [])
    output_files: List[str] = report.get("output_files", [])
    lines = [
        "# 报销运行总结",
        "",
        f"- 执行人: {report.get('user_name', '')}",
        f"- 识别主体: {report.get('primary_entity', '')}",
        f"- 工作餐条目数: {report.get('work_meal_count', 0)}",
        f"- 工作餐原始总额: {report.get('work_meal_total', 0)}",
        f"- 工作餐封顶后总额: {report.get('work_meal_capped_total', 0)}",
        "",
        "## 生成文件",
    ]
    if output_files:
        lines.extend([f"- {path}" for path in output_files])
    else:
        lines.append("- 无")

    lines.extend([
        "",
        "## 建议复核",
    ])
    if review_items:
        lines.extend([f"- {item}" for item in review_items])
    else:
        lines.append("- 无")

    lines.append("")
    lines.append("## 备注")
    if notes:
        lines.extend([f"- {item}" for item in notes])
    else:
        lines.append("- 无")

    return "\n".join(lines) + "\n"


def write_run_report(report: Dict, output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = output_dir / f"reimbursement_run_report_{ts}.md"
    path.write_text(render_run_report(report), encoding="utf-8")
    return path
