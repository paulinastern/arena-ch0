# OfficeQA Verification Checklist

Before returning a final answer, verify every item below.

## Question understanding
- What exact metric is being asked?
- What exact category/entity is being asked?
- What exact period is being asked?
- Does the question ask for a direct value or a computed value?

## Source verification
- Did I identify the correct Treasury Bulletin document?
- Is the document date appropriate for the requested time period?
- Did I find the correct section or table?

## Extraction verification
- Did I choose the correct row?
- Did I choose the correct column?
- Did I verify the full header structure?
- Did I avoid confusing a total with a subtotal or component?
- Did I verify the unit?

## Calculation verification
If calculation is required:
- Did I use only document-supported values?
- Did I apply the correct arithmetic operation?
- Did I double-check the math?
- Did I preserve the proper scale and sign?

## Output verification
- Is the final answer numeric?
- Did I remove extra explanation and words?
- Did I avoid adding units unless explicitly required?
- Does the final number match the verified evidence or computation?

## Common failure warnings
Stop and re-check if:
- two candidate numbers look plausible
- the table has multiple header rows
- the year could be fiscal instead of calendar
- the unit is easy to miss
- the value is a subtotal rather than the requested total
- the answer required arithmetic and the result seems too large or too small