# OfficeQA Common Failure Modes

Use this file to avoid frequent benchmark errors.

## 1. Wrong year or wrong period
The agent finds a relevant table but uses:
- the wrong year
- fiscal year instead of calendar year
- annual total instead of month-end value
- nearby month instead of requested month

Fix:
Always verify the exact date label in the column/header.

## 2. Wrong row due to similar labels
Treasury tables often contain related categories with similar names.

Examples of mistakes:
- choosing "Total receipts" instead of a subcategory
- choosing a neighboring row with similar wording
- choosing a subtotal instead of a grand total

Fix:
Match the requested category exactly.

## 3. Wrong unit
The extracted value is numerically correct on the page but interpreted in the wrong unit.

Examples:
- thousands treated as dollars
- millions treated as billions
- percent treated as raw value

Fix:
Always identify the unit before finalizing.

## 4. Wrong table from keyword match
A keyword search may find a table that mentions the right term but reports a different metric.

Fix:
Check the table title and surrounding context before using the number.

## 5. Table continuation confusion
The agent reads a continuation table without preserving the original column/header context.

Fix:
Reconstruct the full table structure before extracting.

## 6. Narrative-text trap
A paragraph may mention a related number, but the official answer is in the table.

Fix:
Prefer exact table evidence when available.

## 7. Arithmetic on unverified values
The agent performs correct math on the wrong inputs.

Fix:
Verify each input independently before calculating.

## 8. Formatting mistakes
The benchmark may expect only the numeric answer.

Fix:
Output only the final numeric value with no extra words unless explicitly required.

## 9. Rounding or precision drift
The agent rounds too early or changes precision unnecessarily.

Fix:
Keep the precision supported by the source or final computation.