from __future__ import annotations

import re

from app.schemas.advisory import AIAdvisory

UNSAFE_PATTERNS = (
    re.compile(r"\b(?:fraud|fraudulent|guilty|criminal)\b", re.IGNORECASE),
    re.compile(r"\b(?:freeze|block|suspend)\b.{0,30}\baccount\b", re.IGNORECASE),
    re.compile(
        r"\b(?:automatic|automatically)\b.{0,40}\b(?:transfer|refill|settle|reverse)\b",
        re.IGNORECASE,
    ),
    re.compile(r"\bconvert\b.{0,30}\b(?:balance|provider)\b", re.IGNORECASE),
    re.compile(r"\b(?:guaranteed|certain)\b.{0,30}\bshortage\b", re.IGNORECASE),
    re.compile(r"\b(?:resolve|close)\b.{0,30}\bcase\b", re.IGNORECASE),
)


def validate_advisory_safety(advisory: AIAdvisory) -> None:
    text = " ".join(
        [
            advisory.summary,
            advisory.operational_assessment,
            *advisory.why,
            *advisory.uncertainty,
            *advisory.human_verification_questions,
            *(item.title for item in advisory.recommended_actions),
            *(item.rationale for item in advisory.recommended_actions),
            *(item.relevance for item in advisory.source_references),
        ]
    )
    if any(pattern.search(text) for pattern in UNSAFE_PATTERNS):
        raise UnsafeAdvisoryOutputError(
            "Generated advisory language violated an operational safety rule."
        )


class UnsafeAdvisoryOutputError(ValueError):
    pass
