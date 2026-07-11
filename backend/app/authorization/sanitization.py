from __future__ import annotations

import re

from app.core.errors import AppError

PATTERNS = (
    re.compile(r"SIM-ACC-", re.IGNORECASE),
    re.compile(r"\b(?:pin|otp|password|secret|api[_ -]?key)\b", re.IGNORECASE),
    re.compile(r"\b(?:\+?8801|01)[3-9]\d{8}\b"),
)


def validate_workflow_text(value: str) -> str:
    normalized = value.strip()
    if not normalized or any(item.search(normalized) for item in PATTERNS):
        raise AppError(
            status_code=422,
            code="unsafe_workflow_text",
            message="Workflow text contains prohibited or empty content.",
        )
    return normalized
