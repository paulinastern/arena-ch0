from __future__ import annotations

from app.models import CalculationLog, ParsedQuestion


def _to_float(s: str) -> float:
    return float(str(s).strip().replace(",", ""))


def calculate(parsed: ParsedQuestion, values: list[str]) -> CalculationLog:
    op = parsed.get("operation") or "none"
    if op == "none" or len(values) < 2:
        return {
            "inputs": values,
            "operation": op,
            "skipped_reason": "no_operation_or_insufficient_values",
        }
    try:
        a, b = _to_float(values[0]), _to_float(values[1])
    except ValueError:
        return {
            "inputs": values,
            "operation": op,
            "skipped_reason": "non_numeric_inputs",
        }

    result: float | None = None
    if op == "difference":
        result = a - b
    elif op == "sum":
        result = a + b
    elif op == "ratio":
        result = a / b if b != 0 else None

    if result is None:
        return {
            "inputs": [str(values[0]), str(values[1])],
            "operation": op,
            "result": None,
            "skipped_reason": "undefined_result",
        }

    s = f"{result:.10f}".rstrip("0").rstrip(".")
    return {
        "inputs": [str(values[0]), str(values[1])],
        "operation": op,
        "result": s,
    }
