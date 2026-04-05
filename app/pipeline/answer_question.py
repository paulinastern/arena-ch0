from __future__ import annotations

from pathlib import Path

from app import config
from app.models import AnswerTrace
from app.pipeline.calculate import calculate
from app.pipeline.extract import extract
from app.pipeline.format_answer import format_answer
from app.pipeline.parse_question import parse_question
from app.pipeline.retrieve import retrieve
from app.pipeline.verify import verify
from app.utils.io import read_text


def answer_question(question_id: str, question: str, top_k: int = 3) -> AnswerTrace:
    parsed = parse_question(question)
    hits = retrieve(question, parsed.get("keywords") or [], top_k=top_k)

    extraction: dict = {
        "value": None,
        "unit": "",
        "period": "",
        "category": "",
        "evidence": "",
        "table_id": "",
        "confidence": 0.0,
        "error": "no_document",
    }
    doc_excerpt = ""

    if hits:
        top = hits[0]
        doc_excerpt = read_text(Path(top["path"]), limit=200_000)
        extraction = extract(question, parsed, top["path"], doc_excerpt)

    verification = verify(question, parsed, extraction, doc_excerpt)

    calc_log = None
    final_raw: str | None = extraction.get("value")
    values = extraction.get("values")

    if (parsed.get("operation") or "none") != "none" and values and len(values) >= 2:
        calc_log = calculate(parsed, [str(values[0]), str(values[1])])
        if calc_log.get("result") is not None:
            final_raw = calc_log["result"]

    if final_raw is None and extraction.get("value") is not None:
        final_raw = str(extraction["value"])

    if not verification["is_valid"]:
        final_raw = None

    final_answer = format_answer(final_raw) if final_raw is not None else None

    trace: AnswerTrace = {
        "question_id": question_id,
        "final_answer": final_answer,
        "parsed": parsed,
        "retrieval": hits,
        "extraction": extraction,
        "verification": verification,
        "calculation": calc_log,
        "version": config.VERSION,
        "meta": {"corpus_dir": str(config.CORPUS_DIR)},
    }
    return trace
