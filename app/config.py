from __future__ import annotations

import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
CORPUS_DIR = Path(os.environ.get("OFFICEQA_CORPUS_DIR", str(DATA / "corpus")))
RUNS_DIR = Path(os.environ.get("OFFICEQA_RUNS_DIR", str(ROOT / "runs")))
PROMPTS_DIR = ROOT / "prompts"
VERSION = os.environ.get("OFFICEQA_VERSION", "v0_baseline")

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
OPENAI_MODEL = os.environ.get("OFFICEQA_MODEL", "gpt-4o-mini")


def has_llm() -> bool:
    return bool(OPENAI_API_KEY.strip())
