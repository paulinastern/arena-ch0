from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

from app.utils.io import read_jsonl, write_json
from app.utils.normalize import normalize_for_match


def main() -> None:
    p = argparse.ArgumentParser(description="Exact-match scoring (no partial credit).")
    p.add_argument("predictions_path", type=Path)
    p.add_argument("gold_path", type=Path)
    p.add_argument(
        "--out-dir",
        type=Path,
        default=None,
        help="Directory for score.csv and summary (default: parent of predictions).",
    )
    args = p.parse_args()

    out_dir = args.out_dir or args.predictions_path.parent
    out_dir.mkdir(parents=True, exist_ok=True)

    gold: dict[str, str] = {}
    for row in read_jsonl(args.gold_path):
        gold[str(row["question_id"])] = str(row["answer"]).strip()

    pred_map: dict[str, str | None] = {}
    for row in read_jsonl(args.predictions_path):
        pred_map[str(row["question_id"])] = row.get("predicted_answer")

    rows: list[dict] = []
    correct = 0
    total = 0
    for qid, g in sorted(gold.items()):
        total += 1
        pr = pred_map.get(qid)
        ng = normalize_for_match(g)
        npred = normalize_for_match(pr) if pr is not None else ""
        ok = ng == npred and ng != ""
        if ok:
            correct += 1
        rows.append(
            {
                "question_id": qid,
                "gold": g,
                "predicted": pr if pr is not None else "",
                "normalized_gold": ng,
                "normalized_predicted": npred,
                "correct": ok,
                "failure_type": "" if ok else "unclassified",
            }
        )

    score_path = out_dir / "score.csv"
    with score_path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(
            f,
            fieldnames=[
                "question_id",
                "gold",
                "predicted",
                "normalized_gold",
                "normalized_predicted",
                "correct",
                "failure_type",
            ],
        )
        w.writeheader()
        for r in rows:
            w.writerow(r)

    acc = correct / total if total else 0.0
    summary = {"correct": correct, "total": total, "accuracy": acc}
    write_json(out_dir / "score_summary.json", summary)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
