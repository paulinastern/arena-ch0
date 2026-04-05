# OfficeQA Agent

Document-grounded extraction agent for financial table QA: **parse → retrieve → extract → verify → (optional) calculate → format**, with full per-question traces, exact-match scoring, and failure taxonomy for the improvement loop.

## Setup
```bash
pip install -e .
# or: pip install -r requirements.txt
export PYTHONPATH=.
```

Optional LLM extraction: set `OPENAI_API_KEY`. Corpus path defaults to `data/corpus/` (`OFFICEQA_CORPUS_DIR` to override). Without an API key, only documents tagged `OFFICEQA_FIXTURE_TABLE` use the deterministic extractor.

## Run
```bash
python3 -m scripts.run_batch data/batches/batch_001.jsonl --run-id v0_baseline
python3 -m scripts.score_batch runs/v0_baseline/batch_001/predictions.jsonl data/gold/batch_001_gold.jsonl
python3 -m scripts.classify_failures runs/v0_baseline/batch_001
```

Single question:
```bash
echo '{"question_id":"q1","question":"..."}' | PYTHONPATH=. python3 -m app.main
```

## Layout
See repository tree: `app/pipeline/` (stages), `prompts/`, `skills/`, `data/batches`, `data/gold`, `runs/<run_id>/<batch>/traces/`.