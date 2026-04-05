from __future__ import annotations

import re
from pathlib import Path

from app.config import CORPUS_DIR
from app.models import RetrievalHit
from app.utils.io import read_text


def _tokenize(s: str) -> set[str]:
    return set(re.findall(r"[a-z0-9]+", s.lower()))


def retrieve(question: str, keywords: list[str], top_k: int = 3) -> list[RetrievalHit]:
    """
    Keyword overlap scoring over plain-text corpus files (V0).
    Output is inspectable: doc_id, path, score, snippet.
    """
    if not CORPUS_DIR.is_dir():
        return []

    q_tokens = _tokenize(question) | set(keywords)
    hits: list[tuple[float, Path, str]] = []

    for path in sorted(CORPUS_DIR.glob("**/*")):
        if not path.is_file() or path.suffix.lower() not in {".txt", ".md", ".text"}:
            continue
        body = read_text(path, limit=200_000)
        d_tokens = _tokenize(body)
        if not q_tokens:
            score = 0.0
        else:
            inter = len(q_tokens & d_tokens)
            score = float(inter) / max(1, len(q_tokens))
        if score <= 0 and not any(k.lower() in body.lower() for k in keywords[:5] if k):
            continue
        if score <= 0:
            score = 0.01
        snippet = body[:800].replace("\n", " ")
        hits.append((score, path, snippet))

    hits.sort(key=lambda x: x[0], reverse=True)
    out: list[RetrievalHit] = []
    for score, path, snippet in hits[:top_k]:
        out.append(
            {
                "doc_id": path.stem,
                "path": str(path.resolve()),
                "score": round(score, 4),
                "snippet": snippet,
            }
        )
    return out
