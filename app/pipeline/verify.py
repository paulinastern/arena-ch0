from __future__ import annotations

import re

from app.models import ExtractionResult, ParsedQuestion, VerificationResult
from app.utils.normalize import is_numeric_string


def _period_ok(parsed: ParsedQuestion, period: str) -> bool:
    years = parsed.get("years") or []
    if not years:
        return True
    p = (period or "").strip()
    if not p:
        return False
    return all(y in p for y in years) if len(years) > 1 else (years[0] in p)


def _unit_hint_from_question(q: str) -> set[str]:
    t = q.lower()
    hints: set[str] = set()
    if "million" in t:
        hints.add("million")
    if "billion" in t:
        hints.add("billion")
    if "thousand" in t:
        hints.add("thousand")
    if "percent" in t or "%" in t:
        hints.add("percent")
    return hints


def _unit_coherent(question: str, unit: str) -> bool:
    hints = _unit_hint_from_question(question)
    if not hints:
        return True
    u = unit.lower()
    return any(h in u for h in hints)


def _category_overlap(parsed: ParsedQuestion, category: str) -> bool:
    metric = (parsed.get("target_metric") or "").lower()
    cat = category.lower()
    if not metric:
        return bool(cat.strip())
    return metric in cat or cat in metric or any(k in cat for k in parsed.get("keywords", [])[:5])


def verify(
    question: str,
    parsed: ParsedQuestion,
    extraction: ExtractionResult,
    doc_excerpt: str,
) -> VerificationResult:
    warnings: list[str] = []
    value = extraction.get("value")
    values = extraction.get("values")
    unit = extraction.get("unit") or ""
    period = extraction.get("period") or ""
    category = extraction.get("category") or ""
    evidence = extraction.get("evidence") or ""

    if extraction.get("error"):
        warnings.append(f"extraction_error:{extraction['error']}")

    numeric_ok = False
    if value is not None and is_numeric_string(str(value)):
        numeric_ok = True
    elif values and all(is_numeric_string(str(v)) for v in values):
        numeric_ok = True

    period_match = _period_ok(parsed, period)
    if parsed.get("years") and not period:
        period_match = False

    unit_match = _unit_coherent(question, unit)
    category_match = _category_overlap(parsed, category)

    ev = evidence.strip()
    evidence_consistency = bool(ev) and (
        (value is not None and str(value).replace(",", "") in ev.replace(",", ""))
        or bool(values and all(str(v) in ev.replace(",", "") for v in values))
    )
    if value and doc_excerpt and str(value).replace(",", "") in doc_excerpt.replace(",", ""):
        evidence_consistency = evidence_consistency or True

    conf = float(extraction.get("confidence") or 0.0)
    if conf < 0.5:
        warnings.append("low_extraction_confidence")

    checks = {
        "numeric_format": numeric_ok,
        "period_match": period_match,
        "unit_match": unit_match,
        "category_match": category_match,
        "evidence_non_empty": bool(ev),
        "evidence_consistency": evidence_consistency,
        "has_table_id": bool((extraction.get("table_id") or "").strip()),
    }

    is_valid = all(
        [
            checks["numeric_format"],
            checks["period_match"],
            checks["unit_match"],
            checks["category_match"],
            checks["evidence_non_empty"],
            checks["evidence_consistency"],
            checks["has_table_id"],
            conf >= 0.5,
        ]
    )

    if not checks["evidence_non_empty"]:
        warnings.append("missing_evidence")

    return {"is_valid": is_valid, "checks": checks, "warnings": warnings}
