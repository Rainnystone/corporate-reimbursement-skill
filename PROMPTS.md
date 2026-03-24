# Multimodal & Extraction Prompts

These prompts are designed to be used by the AI agent when classifying and extracting data from reimbursement files.

## Prompt 1: Invoice Classification (Zero-Shot)
**Context:** You are an AI assisting in corporate reimbursement.
**Task:** Analyze the provided text (from PDF) or image (screenshot) and the **filename** to classify it into a standardized JSON format.
**Rules:**
1. Identify the Purchaser Header: Match against the recognized corporate entities (e.g., entity BJ or entity SH). If neither, return "UNKNOWN".
2. Identify Category & Dining Details (from Filename & Content):
   - "住宿费" (Hotel)
   - "餐费" (Dining) -> 
     - Check filename for tags: `工作餐` (Work Meal) or `招待/业务餐` (Hospitality).
     - Extract `people_count` from filename (e.g., `1人`, `3人`). Default to 1 if not specified.
     - **Constraint (Work Meal):** Max 80 RMB per person. Final `amount` = `min(Total Amount, people_count * 80)`.
   - "交通费-滴滴" (Didi/Ride-hailing)
   - "交通费-机票" (Flight)
   - "话费" (Phone bill)
3. Extract Amount: The final `价税合计` (Total Amount including tax). **Note:** For "工作餐", apply the per-person cap before returning the JSON amount.
4. Extract Date: The date of the invoice/receipt.
5. Extract Vendor: The selling party.

**Output Format:** JSON only.
```json
{
  "header": "BJ | SH | UNKNOWN",
  "category": "String",
  "amount": 123.45,
  "date": "YYYY-MM-DD",
  "vendor": "String",
  "people_count": 1,
  "original_amount": 150.00,
  "is_capped": true,
  "city": "String (if applicable)"
}
```

## Prompt 2: Didi Trip Table Analysis (Vision/Text)
**Context:** This is a ride-hailing "Trip Table" (行程单), not the actual invoice.
**Task:** Extract the total amount, city, and date range.
**Rules:** 
- Look for the column "城市" (City).
- Look for "合计 X 元" (Total amount).
- We use this to link to the corresponding electronic invoice.

## Prompt 3: Ignorable Files Detection
**Task:** Is this image just a supplementary screenshot (like a McDonald's order summary) without an actual formal invoice layout? 
**Output:** Boolean (true if ignorable, false if it's a real invoice).
