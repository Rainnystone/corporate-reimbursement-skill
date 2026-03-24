# Reimbursement Skill Self-Correction Log

| Run # | Date | Result | Key Issues Found | Adjustments Made |
|-------|------|--------|------------------|------------------|
| 0 | 2026-03-24 | FAIL | Engine is a mock; does not write data. | Created infrastructure for automated comparison. |
| 1 | 2026-03-24 | FAIL | 1. Mapped columns incorrectly. 2. Overwrote formula in J4. 3. Cover page total rows mismatch. | 1. Updated population logic to match benchmark rows/columns. 2. Added tax calculation. 3. Added unmerge utility. |
| 2 | 2026-03-24 | PARTIAL | 1. Benchmark has customized row counts. 2. Missed personal data (Payee/Bank). | 1. Implemented Anchor Detection logic. 2. Implemented 80 RMB/person work meal cap. 3. Added category ordering logic. |

## Major Findings
- **Template Customization:** The benchmark files use a customized version of the template.
- **Privacy Scrubbing:** Systematically removed all specific company identifiers (including acronyms) and personal details to prepare for GitHub.
- **Work Meal Cap:** Successfully extracted person count from filenames and applied the 80 RMB limit.
