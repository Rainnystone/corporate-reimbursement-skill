# Corporate Reimbursement Automation Skill

Automated expense reimbursement processing for complex corporate Excel templates. This skill uses Multimodal AI and OCR to classify invoices, apply corporate policies (like meal caps), and populate structured Excel reports while preserving formula integrity.

## ⚠️ Important Requirements

1.  **Multimodal Capabilities (Mandatory):** Ensure the LLM executing this skill has vision/multimodal capabilities to accurately process invoice images and document layouts.
2.  **Invoice Labeling:** To accurately apply policy limits, dining invoices (PDF/JPG) **MUST** be labeled in the filename with their purpose and person count.
    *   **Tags:** 工作餐 (Work Meal) or 招待 (Hospitality).
    *   **Count:** X人 or Xppl.
    *   *Example:* Lunch with Client 3ppl.pdf or 0108 工作餐 3人.pdf

## Compatibility
This skill is designed to be **platform-agnostic** and can be used by any AI-powered CLI agent that supports custom instructions/skills, including:
- **Gemini CLI**
- **Claude Code**
- **Codex**
- **Any Agentic Workflow** supporting Python execution.

## Features
- **Intelligent Classification:** Differentiates between Hotel, Dining (Work vs. Hospitality), Transport (Didi/Flight), and Phone bills.
- **Meal Policy Enforcement:** Automatically applies a per-person cap (default: 80 RMB) for work meals based on filename tags.
- **Formula Preservation:** Safely writes data to templates without overwriting existing Excel formulas.
- **Layout Resiliency:** Uses anchor-based row detection to handle customized template layouts.

## Prerequisites

### Dependencies
Install the required libraries:
\`\`\`bash
pip install openpyxl docling pandas
\`\`\`

## Installation (Universal)
1. Clone this repository.
2. Register the folder in your AI agent's skills/extensions directory.
3. Ensure the `engine/check_env.py` script is executable.

## Local Configuration
Edit `engine/config.py` to match your local corporate entity names.

## Usage
### Via AI Agent
> "Use the corporate-reimbursement skill to process invoices in './Jan_2026' using the template 'template.xlsx'."

### Via Command Line
\`\`\`bash
PYTHONPATH=. python3 reimburse.py --input-dir <invoices_folder> --template <template.xlsx> --output-dir <output_folder>
\`\`\`

## License
MIT
