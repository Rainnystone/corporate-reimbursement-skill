# Skill Design: Corporate Reimbursement

## Objective
To provide a robust AI skill that transforms raw invoice data into structured financial reports (Excel) while adhering to strict corporate policies.

## Implementation Details
- **Extraction:** Powered by multimodal LLMs and `docling` for OCR.
- **Mapping:** Dynamic mapping of expense types to specific sheets and rows.
- **Layout Resiliency:** Anchor-based detection to handle customized template layouts.
- **Policy Enforcement:** Rules for per-person limits on dining expenses.
