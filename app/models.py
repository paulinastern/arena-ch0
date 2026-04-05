from __future__ import annotations

from typing import Any, NotRequired, TypedDict


class ParsedQuestion(TypedDict, total=False):
    raw: str
    target_metric: str | None
    year: str | None
    years: list[str]
    quarter: str | None
    operation: str  # "none" | "difference" | "sum" | "ratio"
    keywords: list[str]


class RetrievalHit(TypedDict):
    doc_id: str
    path: str
    score: float
    snippet: str


class ExtractionResult(TypedDict, total=False):
    value: str | None
    values: list[str] | None
    unit: str
    period: str
    category: str
    evidence: str
    table_id: str
    confidence: float
    error: str
    doc_id: str


class VerificationResult(TypedDict):
    is_valid: bool
    checks: dict[str, bool]
    warnings: list[str]


class CalculationLog(TypedDict, total=False):
    inputs: list[str]
    operation: str
    result: str | None
    skipped_reason: str


class AnswerTrace(TypedDict, total=False):
    question_id: str
    final_answer: str | None
    parsed: ParsedQuestion
    retrieval: list[RetrievalHit]
    extraction: ExtractionResult
    verification: VerificationResult
    calculation: CalculationLog | None
    version: str
    meta: NotRequired[dict[str, Any]]
