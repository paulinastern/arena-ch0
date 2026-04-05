from __future__ import annotations

import json
import re
from pathlib import Path

from app import config
from app.models import ExtractionResult, ParsedQuestion
from app.utils.io import read_text


def _load_prompt(name: str) -> str:
    p = config.PROMPTS_DIR / name
    if not p.is_file():
        return ""
    return p.read_text(encoding="utf-8")


def _fixture_extract(doc_text: str, parsed: ParsedQuestion) -> ExtractionResult | None:
    """
    Deterministic path for offline tests: documents tagged OFFICEQA_FIXTURE_TABLE.
    Simple pipe table: Row|Col1951|Col1952
    """
    if "OFFICEQA_FIXTURE_TABLE" not in doc_text:
        return None
    year = parsed.get("year") or (parsed.get("years") or [None])[0]
    if not year:
        return None
    lines = [ln.strip() for ln in doc_text.splitlines() if "|" in ln]
    if len(lines) < 2:
        return None
    header = [c.strip() for c in lines[0].split("|")]
    try:
        yi = header.index(year)
    except ValueError:
        return None
    keys = [k.lower() for k in parsed.get("keywords") or [] if k]
    best_row: list[str] | None = None
    for ln in lines[1:]:
        cells = [c.strip() for c in ln.split("|")]
        if len(cells) <= yi:
            continue
        row_label = cells[0].lower()
        if any(k in row_label for k in keys[:8]):
            best_row = cells
            break
    if best_row is None:
        for ln in lines[1:]:
            cells = [c.strip() for c in ln.split("|")]
            if len(cells) > yi:
                best_row = cells
                break
    if not best_row:
        return None
    val = re.sub(r"[^\d.\-]", "", best_row[yi])
    if not val:
        return None
    return {
        "value": val,
        "unit": "millions of dollars",
        "period": year,
        "category": best_row[0],
        "evidence": f"Fixture row '{best_row[0]}' column '{header[yi]}' = {val}",
        "table_id": "fixture_main",
        "confidence": 1.0,
        "doc_id": "fixture",
    }


def _llm_extract(question: str, doc_path: str, doc_text: str, parsed: ParsedQuestion) -> ExtractionResult:
    try:
        from openai import OpenAI
    except ImportError:
        return {
            "value": None,
            "unit": "",
            "period": "",
            "category": "",
            "evidence": "",
            "table_id": "",
            "confidence": 0.0,
            "error": "openai package not installed",
        }

    system = _load_prompt("extraction_prompt.txt")
    skills_hint = ""
    for name in ("table_reading.md", "verification_checklist.md"):
        sp = config.ROOT / "skills" / name
        if sp.is_file():
            skills_hint += sp.read_text(encoding="utf-8")[:4000] + "\n"

    client = OpenAI(api_key=config.OPENAI_API_KEY)
    user = json.dumps(
        {
            "question": question,
            "parsed": parsed,
            "document_path": doc_path,
            "document_excerpt": doc_text[:14_000],
            "skills_excerpt": skills_hint[:6000],
        },
        ensure_ascii=False,
    )
    resp = client.chat.completions.create(
        model=config.OPENAI_MODEL,
        temperature=0,
        messages=[
            {"role": "system", "content": system or "Return only valid JSON."},
            {"role": "user", "content": user},
        ],
        response_format={"type": "json_object"},
    )
    content = resp.choices[0].message.content or "{}"
    data = json.loads(content)
    def g(k: str, default: str = "") -> str:
        v = data.get(k)
        return default if v is None else str(v)

    vals = data.get("values")
    if vals is not None and not isinstance(vals, list):
        vals = None
    out: ExtractionResult = {
        "value": g("value") or None,
        "unit": g("unit"),
        "period": g("period"),
        "category": g("category"),
        "evidence": g("evidence"),
        "table_id": g("table_id"),
        "confidence": float(data.get("confidence", 0.0) or 0.0),
        "doc_id": Path(doc_path).stem,
    }
    if vals:
        out["values"] = [str(x) for x in vals]
    return out


def extract(
    question: str,
    parsed: ParsedQuestion,
    doc_path: str,
    doc_text: str,
) -> ExtractionResult:
    fix = _fixture_extract(doc_text, parsed)
    if fix is not None:
        fix["doc_id"] = Path(doc_path).stem
        return fix

    if config.has_llm():
        return _llm_extract(question, doc_path, doc_text, parsed)

    return {
        "value": None,
        "unit": "",
        "period": "",
        "category": "",
        "evidence": "",
        "table_id": "",
        "confidence": 0.0,
        "error": "No LLM configured and document is not a deterministic fixture.",
    }
