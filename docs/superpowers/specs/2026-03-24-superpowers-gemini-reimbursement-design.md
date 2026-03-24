# Corporate Reimbursement Design Spec

## Overview
This suite automates the "Corporate Payment Application" process. It handles multiple company headers (BJ/SH), classifies expenses (Hotel, Dining, Transport), and maintains Excel formula integrity across multiple sheets.

## Key Features
- **Header Detection:** Automatic classification of invoices based on the purchaser name.
  - `ENTITY_BJ_NAME` -> `BJ.xlsx`
  - `ENTITY_SH_NAME` -> `SH.xlsx`
- **Dynamic Calculation:** Handles tax logic (e.g., 3% for Didi, 9% for Ticket portions).
- **Formula Protection:** Uses a `safe_write` mechanism to avoid corrupting Excel template formulas.
- **Auto-Correction Loop:** Integrated test suite to compare AI output against benchmarks.
- **Work Meal Capping:** Automatic enforcement of the 80 RMB per person limit for work meals.
