---
name: auto-reimbursement-automation
description: Automates the extraction and filling of corporate payment application Excel files from invoices (PDFs/Images).
---

# Corporate Reimbursement Automation Skill

## Pre-flight Check (MANDATORY)
Before processing any files, the agent MUST run the environment check script to ensure all dependencies (`docling`, `openpyxl`) are installed:
```bash
python3 engine/check_env.py
```
If the check fails, report the missing dependencies to the user and stop.


This skill is designed to process reimbursement materials (invoices, receipts, trip tables) and populate complex payment application Excel templates, correctly handling different company headers, tax calculations, and dynamic formula protection.

## Workflow

When the user asks to process reimbursements for a given folder:

### Phase 0: Guided Local Setup (First Run / `--setup`)
1. On first run (or when user requests reset), ask and save locally:
   - 报销主体全名或关键字
   - 工作餐默认人数
   - 工作餐常见最大人数
2. Save per-user local profile to `~/.reimburse/profiles/<user>.json`.
3. Never write personal/company runtime data into repository files.

### Phase 1: Classification & Preparation
1. Scan the input directory for all files (PDFs, JPGs, OFDs).
2. Note: If an `.ofd` file is present, look for a corresponding `.pdf` and use the PDF. If no PDF exists, ask the user if they can provide one, as `docling` does not support OFD.
3. Use your **Multimodal Vision** capabilities (or `docling` for PDFs) to classify each file based on the prompts defined in `PROMPTS.md`. 
   - **Category:** Hotel, Dining (Work/Business/Travel), Transport (Flight/Didi/Taxi), Phone.
   - **Entity:** Infer corporate entity from invoice text (entity-agnostic; do not assume BJ/SH only).
   - **Date & Amount.**
4. If travel-application files are present, extract **出发城市/目的城市/出差事由** and use concise summaries for flight details (e.g., `机票费（城市A-城市B：客户拜访）`).
5. Dining categorization must use folder structure:
   - `input/工作餐/`
   - `input/招待/`
6. **Unknown entity handling (hard rule):**
   - If entity is unknown, run a second-pass check using semantic context + multimodal clues.
   - If still uncertain, assign to a configured entity bucket with explicit review note.
   - Do not emit `UNKNOWN_ENTITY` as a final output bucket.

### Phase 2: Engine Invocation
Once you have mapped the logic (which files belong to which header, and what their parsed values are), you will invoke the Python automation engine to do the heavy lifting of writing to Excel safely without breaking formulas.

Run the engine script (assuming you have already mapped data internally or pass it via JSON):
```bash
python3 reimburse.py --input-dir <path> --template "TEMPLATE_FILE.xlsx" --output-dir <path>
```

### Phase 3: Validation
After the engine completes:
1. Verify that the output Excel files are created in the output directory.
2. Open the generated Excel using `pandas` or `openpyxl` to spot-check that totals align with the original PDF sums.
3. Show work-meal list and allow post-run headcount correction with compact reply format (`2,3,2...`).
4. Output a terminal summary and save report file path for user follow-up.

## Critical Constraints
- **Do not overwrite formulas:** The Excel template uses automatic calculations. You must rely on `engine/excel_engine.py`'s `safe_write` method.
- **Dynamic Row Insertion:** Different months have different numbers of entries. If you run out of pre-allocated rows, you MUST instruct the engine to dynamically insert new rows BEFORE writing.
- **Ride-hailing Parsing:** Link the Trip Table (行程单) for city routing to the Invoice (电子发票) for the tax header.
- **Entity Generalization:** Prefer semantic extraction from invoice text over static city/company mapping.
- **Dining Splitting & Limits:** 
  - **Source of Truth:** Use folder placement (`工作餐`/`招待`) and post-run headcount confirmation as the primary source.
  - **Work Meal Limit (工作餐):** There is a hard limit of **80 RMB per person**. 
    - Calculation: `Reimbursable Amount = min(Total Invoice Amount, Number of People * 80)`.
    - If the invoice amount exceeds the limit, only the capped amount (`People * 80`) should be entered into the Excel.
  - **Entertainment/Hospitality (招待/业务餐):** No per-person limit. Use the full invoice amount.
  - **Mismatch Handling:** If user-provided headcount count does not match item count, first attempt amount-based temporary matching and ask for confirmation/complete list.
