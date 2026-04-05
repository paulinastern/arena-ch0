from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

from app.utils.io import write_json
from app.utils.normalize import normalize_for_match


FAILURE_TYPES = (
    "retrieval_error",
    "wrong_table",
    "wrong_row_column",
    "unit_error",
    "arithmetic_error",
    "formatting_error",
    "verification_miss",
)


def classify_from_trace(trace: dict, gold_norm: str, pred_norm: str) -> str:
    """Assign exactly one failure label for an incorrect example."""
    if pred_norm == "":
        retr = trace.get("retrieval") or []
        if not retr:
            return "retrieval_error"
        ext = trace.get("extraction") or {}
        if ext.get("error"):
            return "retrieval_error"

    ver = trace.get("verification") or {}
    checks = ver.get("checks") or {}
    parsed = trace.get("parsed") or {}
    calc = trace.get("calculation") or {}

    if not ver.get("is_valid", False):
        ext_early = trace.get("extraction") or {}
        if checks.get("numeric_format") is False:
            if normalize_for_match(str(ext_early.get("value") or "")) == gold_norm and gold_norm:
                return "formatting_error"
        if checks.get("unit_match") is False:
            return "unit_error"
        if checks.get("period_match") is False or checks.get("category_match") is False:
            return "wrong_row_column"
        if checks.get("evidence_consistency") is False or checks.get("evidence_non_empty") is False:
            return "verification_miss"
        return "verification_miss"

    if parsed.get("operation") not in (None, "none") and calc.get("skipped_reason"):
        return "arithmetic_error"
    if parsed.get("operation") not in (None, "none") and calc.get("result"):
        if gold_norm != pred_norm:
            return "arithmetic_error"

    ext = trace.get("extraction") or {}
    if ext.get("table_id") == "" and pred_norm:
        return "wrong_table"

    if pred_norm and gold_norm and pred_norm != gold_norm:
        if normalize_for_match(str(ext.get("value") or "")) == gold_norm:
            return "formatting_error"

    return "wrong_row_column"


def main() -> None:
    p = argparse.ArgumentParser(description="Label incorrect rows using saved traces.")
    p.add_argument("run_dir", type=Path, help="e.g. runs/v0_baseline/batch_001")
    args = p.parse_args()

    score_csv = args.run_dir / "score.csv"
    traces_dir = args.run_dir / "traces"
    if not score_csv.is_file():
        raise SystemExit(f"Missing {score_csv}; run scripts.score_batch first.")

    out_rows: list[dict] = []
    counts: dict[str, int] = {k: 0 for k in FAILURE_TYPES}

    with score_csv.open(encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            qid = row["question_id"]
            correct = row.get("correct", "").lower() in ("1", "true", "yes")
            if correct:
                row["failure_type"] = ""
                out_rows.append(row)
                continue

            tpath = traces_dir / f"{qid}.json"
            if not tpath.is_file():
                row["failure_type"] = "retrieval_error"
                counts["retrieval_error"] += 1
                out_rows.append(row)
                continue

            trace = json.loads(tpath.read_text(encoding="utf-8"))
            label = classify_from_trace(
                trace,
                row.get("normalized_gold", ""),
                row.get("normalized_predicted", ""),
            )
            if label not in FAILURE_TYPES:
                label = "wrong_row_column"
            row["failure_type"] = label
            counts[label] += 1
            out_rows.append(row)

    out_csv = args.run_dir / "score_classified.csv"
    with out_csv.open("w", encoding="utf-8", newline="") as f:
        fieldnames = list(out_rows[0].keys()) if out_rows else []
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in out_rows:
            w.writerow(r)

    write_json(args.run_dir / "failure_summary.json", {"counts": counts})
    print(json.dumps({"wrote": str(out_csv), "counts": counts}, indent=2))


if __name__ == "__main__":
    main()
