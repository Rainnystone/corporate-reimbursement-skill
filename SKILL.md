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

### Phase 1: Classification & Preparation
1. Scan the input directory for all files (PDFs, JPGs, OFDs).
2. Note: If an `.ofd` file is present, look for a corresponding `.pdf` and use the PDF. If no PDF exists, ask the user if they can provide one, as `docling` does not support OFD.
3. Use your **Multimodal Vision** capabilities (or `docling` for PDFs) to classify each file based on the prompts defined in `PROMPTS.md`. 
   - **Category:** Hotel, Dining (Work/Business/Travel), Transport (Flight/Didi/Taxi), Phone.
   - **Header:** Group by recognized corporate entity (e.g., BJ vs SH).
   - **Date & Amount.**

### Phase 2: Engine Invocation
Once you have mapped the logic (which files belong to which header, and what their parsed values are), you will invoke the Python automation engine to do the heavy lifting of writing to Excel safely without breaking formulas.

Run the engine script (assuming you have already mapped data internally or pass it via JSON):
```bash
python3 reimbursement_engine.py --input-dir <path> --template "TEMPLATE_FILE.xlsx" --output-dir <path>
```

### Phase 3: Validation
After the engine completes:
1. Verify that the output Excel files are created in the output directory.
2. Open the generated Excel using `pandas` or `openpyxl` to spot-check that totals align with the original PDF sums.

## Critical Constraints
- **Do not overwrite formulas:** The Excel template uses automatic calculations. You must rely on `reimbursement/excel_engine.py`'s `safe_write` method.
- **Dynamic Row Insertion:** Different months have different numbers of entries. If you run out of pre-allocated rows, you MUST instruct the engine to dynamically insert new rows BEFORE writing.
- **Ride-hailing Parsing:** Link the Trip Table (行程单) for city routing to the Invoice (电子发票) for the tax header.
- **Dining Splitting & Limits:** 
  - **Source of Truth:** Use filename tags (e.g., `工作餐`, `招待`) and number of people (e.g., `1人`, `3人`) as the primary source of truth for categorization.
  - **Work Meal Limit (工作餐):** There is a hard limit of **80 RMB per person**. 
    - Calculation: `Reimbursable Amount = min(Total Invoice Amount, Number of People * 80)`.
    - If the invoice amount exceeds the limit, only the capped amount (`People * 80`) should be entered into the Excel.
  - **Entertainment/Hospitality (招待/业务餐):** No per-person limit. Use the full invoice amount.
  - **Default Logic:** If no tag is present in the filename, default to "工作餐" if at home base and not traveling, "差旅餐" if out-of-town.
