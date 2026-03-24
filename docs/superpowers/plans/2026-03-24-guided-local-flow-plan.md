# Guided Local Workflow Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a colleague-friendly guided reimbursement workflow with local private profile storage, folder-based dining classification, headcount correction loop, and run report output.

**Architecture:** Extend the current CLI entrypoint with a guided setup/load phase and a reporting phase while keeping extraction/writing separated. Add focused modules for local profile persistence, guided parsing/matching logic, and report rendering. Keep personal/company data outside the repository by storing profile/report metadata in user home.

**Tech Stack:** Python 3, unittest, pathlib/json, existing docling/openpyxl flow.

---

### Task 1: Local Profile Storage (Per User, Local Only)

**Files:**
- Create: `engine/local_profile.py`
- Test: `tests/test_local_profile.py`

- [ ] **Step 1: Write failing tests for load/save and per-user profile behavior**
- [ ] **Step 2: Run targeted test to verify fail**
- [ ] **Step 3: Implement minimal profile persistence in user home (default `~/.reimburse/profiles/<user>.json`)**
- [ ] **Step 4: Run targeted test to verify pass**

### Task 2: Guided Input Parsing and Fallback Matching

**Files:**
- Create: `engine/guided.py`
- Test: `tests/test_guided.py`

- [ ] **Step 1: Write failing tests for parsing `2,3、2` format and amount-based fallback mapping**
- [ ] **Step 2: Run targeted test to verify fail**
- [ ] **Step 3: Implement parser and mismatch fallback matching**
- [ ] **Step 4: Run targeted test to verify pass**

### Task 3: Report Generation (Terminal + File)

**Files:**
- Create: `engine/reporting.py`
- Test: `tests/test_reporting.py`

- [ ] **Step 1: Write failing tests for report text rendering and file write**
- [ ] **Step 2: Run targeted test to verify fail**
- [ ] **Step 3: Implement report rendering and file output helper**
- [ ] **Step 4: Run targeted test to verify pass**

### Task 4: CLI Orchestration Integration

**Files:**
- Modify: `reimburse.py`
- Modify: `engine/semantic.py` (small helper additions if needed)
- Test: `tests/test_cli_flow.py` (focused unit tests on pure helpers only)

- [ ] **Step 1: Add setup trigger (`first run` or `--setup`) and folder-based meal classification**
- [ ] **Step 2: Add default headcount flow + post-run correction input handling**
- [ ] **Step 3: Add primary entity selection using configured base company keywords + semantic grouping**
- [ ] **Step 4: Add summary output and report file location print**
- [ ] **Step 5: Run focused tests for new helper logic**

### Task 5: Documentation Update

**Files:**
- Modify: `README.md`
- Modify: `SKILL.md`

- [ ] **Step 1: Update usage to guided setup and folder rules (`input/工作餐`, `input/招待`)**
- [ ] **Step 2: Document local-only profile storage path and privacy boundary**
- [ ] **Step 3: Document report output and headcount correction reply format**

### Task 6: Final Verification

**Files:**
- Verify: `tests/*`

- [ ] **Step 1: Run full test suite (`python3 -m unittest discover -s tests -v`)**
- [ ] **Step 2: Run env check (`python3 engine/check_env.py`)**
- [ ] **Step 3: Confirm no temporary artifacts and clean status review**
