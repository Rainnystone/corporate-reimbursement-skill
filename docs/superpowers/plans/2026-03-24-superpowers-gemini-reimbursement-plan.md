# Reimbursement Automation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a Python-based automation engine and accompanying AI Skill to extract reimbursement data from PDFs/Images and populate complex Excel templates.

**Architecture:** A Python orchestration script (`reimbursement_engine.py`) drives the workflow: classifying files, extracting data via Docling/Vision API, and safely writing to an Excel template using `openpyxl` to preserve formulas. A `SKILL.md` provides the agentic entry point.

**Tech Stack:** Python 3, `docling`, `pandas`, `openpyxl`, `google-genai` (or equivalent for multimodal), Claude Code / Gemini CLI.

---

### Task 1: Project Scaffolding & Configuration

**Files:**
- Create: `engine/config.py`
- Create: `engine/utils.py`
- Create: `tests/test_config.py`

- [ ] **Step 1: Write configuration tests**
```python
def test_config_constants():
    from engine.config import HEADERS, EXCEL_MAPPING
    assert "BJ" in HEADERS
    assert "SH" in HEADERS
    assert "国内差旅详单" in EXCEL_MAPPING["sheets"]
```

- [ ] **Step 2: Run test to verify it fails**
Run: `pytest tests/test_config.py`
Expected: FAIL with ModuleNotFoundError

- [ ] **Step 3: Implement config and utils**
Create `config.py` with standard mapping dictionaries (Headers -> Excel suffix, Sheet names, row anchors). Create `utils.py` for standard logging setup.

- [ ] **Step 4: Run test to verify it passes**
Run: `pytest tests/test_config.py`
Expected: PASS

- [ ] **Step 5: Commit**
```bash
git add engine/config.py engine/utils.py tests/test_config.py
git commit -m "feat: setup project structure and configuration"
```

### Task 2: Implement `Excel-Engine` (Template Writer)

**Files:**
- Create: `engine/excel_engine.py`
- Create: `tests/test_excel_engine.py`

- [ ] **Step 1: Write test for formula protection**
```python
def test_formula_protection(tmp_path):
    from engine.excel_engine import safe_write
    # Create dummy workbook with formula
    # Try to overwrite formula cell -> assert skipped
    # Try to overwrite empty cell -> assert written
```

- [ ] **Step 2: Run test to verify it fails**
Run: `pytest tests/test_excel_engine.py`
Expected: FAIL

- [ ] **Step 3: Implement `safe_write` and template loading**
Implement logic in `excel_engine.py` using `openpyxl` to check `cell.data_type != 'f'` before writing, and handle dynamic row offsets based on category.

- [ ] **Step 4: Run test to verify it passes**
Run: `pytest tests/test_excel_engine.py`
Expected: PASS

- [ ] **Step 5: Commit**
```bash
git add engine/excel_engine.py tests/test_excel_engine.py
git commit -m "feat: implement formula-safe excel writer"
```

### Task 3: Implement `Data-Extractor` (Docling wrapper)

**Files:**
- Create: `engine/extractor.py`
- Create: `tests/test_extractor.py`

- [ ] **Step 1: Write extraction test**
```python
def test_docling_extraction():
    from engine.extractor import extract_pdf_text
    # Mock docling converter or use a tiny sample PDF
    text = extract_pdf_text("sample.pdf")
    assert type(text) == str
```

- [ ] **Step 2: Run test to verify it fails**
Run: `pytest tests/test_extractor.py`
Expected: FAIL

- [ ] **Step 3: Implement Docling wrapper**
Implement `extract_pdf_text` using `docling.document_converter.DocumentConverter`. Export to Markdown.

- [ ] **Step 4: Run test to verify it passes**
Run: `pytest tests/test_extractor.py`
Expected: PASS

- [ ] **Step 5: Commit**
```bash
git add engine/extractor.py tests/test_extractor.py
git commit -m "feat: implement docling pdf text extractor"
```

### Task 4: Implement Workflow Orchestrator

**Files:**
- Create: `reimbursement_engine.py`
- Modify: `engine/config.py`

- [ ] **Step 1: Implement main CLI script**
Write `reimbursement_engine.py` using `argparse` to accept `--input-dir`, `--template`, and `--output-dir`. Connect Extractor -> Excel Engine.

- [ ] **Step 2: Dry-run the script against sample set**
Run script on `sample set/sample 2 202510/input` (print logic only, no write).
Expected: Outputs parsed mapping.

- [ ] **Step 3: Commit**
```bash
git add reimbursement_engine.py
git commit -m "feat: create main reimbursement CLI orchestrator"
```

### Task 5: Create the AI Skill Definition

**Files:**
- Create: `SKILL.md`
- Create: `PROMPTS.md`

- [ ] **Step 1: Write `SKILL.md`**
Define the skill instructions instructing Claude/Gemini how to invoke `reimbursement_engine.py`, how to use vision models for JPGs, and how to handle errors.

- [ ] **Step 2: Write `PROMPTS.md`**
Define the system prompts required for the LLM to accurately extract "Purchaser", "Date", "Amount", and "City" from raw Docling Markdown output or images.

- [ ] **Step 3: Commit**
```bash
git add SKILL.md PROMPTS.md
git commit -m "docs: add AI skill instructions and prompts"
```
