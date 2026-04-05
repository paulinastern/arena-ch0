from __future__ import annotations

import re


def normalize_for_match(s: str | None) -> str:
    """Normalize predicted/gold answers for exact match (no partial credit)."""
    if s is None:
        return ""
    t = str(s).strip()
    t = t.replace(",", "")
    t = re.sub(r"\s+", "", t)
    if t == "-0":
        t = "0"
    if re.fullmatch(r"-?\d+\.\d+", t):
        t = t.rstrip("0").rstrip(".")
    return t


def is_numeric_string(s: str) -> bool:
    if not s:
        return False
    return bool(re.fullmatch(r"-?\d+(\.\d+)?", s.strip().replace(",", "")))
