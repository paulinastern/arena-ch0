from __future__ import annotations

import argparse
import json
from pathlib import Path

from app import config
from app.pipeline.answer_question import answer_question
from app.utils.io import read_jsonl, write_json, write_jsonl


def main() -> None:
    p = argparse.ArgumentParser(description="Run OfficeQA pipeline on a JSONL batch.")
    p.add_argument("batch_path", type=Path, help="Path to batch JSONL (question_id, question).")
    p.add_argument("--run-id", default=None, help="Run folder name (default: OFFICEQA_VERSION).")
    p.add_argument("--top-k", type=int, default=3, help="Retrieve top-k documents.")
    args = p.parse_args()

    run_id = args.run_id or config.VERSION
    batch_name = args.batch_path.stem
    out_dir = config.RUNS_DIR / run_id / batch_name
    traces_dir = out_dir / "traces"
    traces_dir.mkdir(parents=True, exist_ok=True)

    preds: list[dict] = []
    for row in read_jsonl(args.batch_path):
        qid = row["question_id"]
        question = row["question"]
        trace = answer_question(qid, question, top_k=args.top_k)
        write_json(traces_dir / f"{qid}.json", trace)
        preds.append(
            {
                "question_id": qid,
                "predicted_answer": trace.get("final_answer"),
            }
        )

    write_jsonl(out_dir / "predictions.jsonl", preds)
    write_json(
        out_dir / "run_meta.json",
        {
            "version": config.VERSION,
            "run_id": run_id,
            "batch": batch_name,
            "batch_path": str(args.batch_path.resolve()),
            "corpus_dir": str(config.CORPUS_DIR),
            "top_k": args.top_k,
        },
    )
    print(json.dumps({"output_dir": str(out_dir), "n": len(preds)}, indent=2))


if __name__ == "__main__":
    main()
