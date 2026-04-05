from __future__ import annotations

import re

from app.models import ParsedQuestion


_YEAR = re.compile(r"\b(?:19|20)\d{2}\b")
_QUARTER = re.compile(r"\bQ[1-4]\b", re.I)


def parse_question(question: str) -> ParsedQuestion:
    text = question.strip()
    years: list[str] = []
    for m in _YEAR.finditer(text):
        years.append(m.group(0))
    years = sorted(set(years))
    qm = _QUARTER.search(text)
    quarter = qm.group(0).upper() if qm else None

    op = "none"
    tl = text.lower()
    if any(k in tl for k in ("difference", "minus", "subtract", "less")):
        op = "difference"
    elif "ratio" in tl or "divide" in tl or " per " in tl:
        op = "ratio"
    elif "sum" in tl or "total of" in tl or "combined" in tl:
        op = "sum"

    stop = {
        "what", "the", "in", "for", "of", "is", "are", "was", "were", "how", "much",
        "many", "from", "to", "between", "and", "or", "a", "an", "by", "as", "at",
        "on", "with", "value", "amount", "table", "treasury", "bulletin", "fiscal",
        "year", "calendar", "quarter", "million", "billions", "thousands", "dollars",
    }
    words = re.findall(r"[A-Za-z]{3,}", text.lower())
    keywords = [w for w in words if w not in stop][:12]

    year = years[0] if len(years) == 1 else None
    target_metric: str | None = None
    if keywords:
        target_metric = keywords[0]

    return {
        "raw": text,
        "target_metric": target_metric,
        "year": year,
        "years": years,
        "quarter": quarter,
        "operation": op,
        "keywords": keywords,
    }
