from __future__ import annotations

import re

from app.utils.normalize import normalize_for_match


def format_answer(raw: str | None) -> str | None:
    """
    Final benchmark answer: numeric only, no units, commas removed unless
    required by spec (here: strip commas for normalization consistency with scorer).
    """
    if raw is None:
        return None
    t = str(raw).strip()
    t = t.replace(",", "")
    m = re.search(r"-?\d+(?:\.\d+)?", t)
    if not m:
        return None
    return normalize_for_match(m.group(0))
