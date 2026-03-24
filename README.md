# Corporate Reimbursement Extension

Automated expense reimbursement processing for corporate Excel templates.

## Setup
1. Fill in `engine/config.py` with your actual corporate entity names.
2. Ensure `openpyxl` and `docling` are installed.

## Usage
Run via Gemini CLI or manually:
```bash
python3 reimburse.py --input-dir <invoices_folder> --template <excel_template> --output-dir <output_folder>
```
