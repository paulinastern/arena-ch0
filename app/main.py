from __future__ import annotations

import argparse
import json
import sys

from app.pipeline.answer_question import answer_question


def main() -> None:
    p = argparse.ArgumentParser(description="Run pipeline for one question (stdin JSON or CLI args).")
    p.add_argument("--question-id", default="cli")
    p.add_argument("--question", default=None)
    args = p.parse_args()

    if args.question is not None:
        q = args.question
        qid = args.question_id
    else:
        payload = json.loads(sys.stdin.read())
        qid = payload.get("question_id", "stdin")
        q = payload["question"]

    trace = answer_question(qid, q)
    json.dump(trace, sys.stdout, indent=2, ensure_ascii=False)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
