from __future__ import annotations

import re

from app.db.models import PolicySnippet, SimilarCaseSummary
from app.repositories.alert_repository import AlertRepository
from app.schemas.alert import RetrievalSource
from app.schemas.enums import AlertType, Provider, Severity


class RetrievalService:
    def __init__(self, repository: AlertRepository) -> None:
        self._repository = repository

    def retrieve(
        self,
        *,
        alert_type: AlertType,
        provider: Provider,
        severity: Severity,
        reasons: list[str],
    ) -> tuple[list[RetrievalSource], list[RetrievalSource]]:
        terms = _terms(" ".join(reasons)) | {
            provider.value.lower(),
            alert_type.value.lower(),
            severity.value.lower(),
        }
        policies = sorted(
            self._repository.list_policy_snippets(),
            key=lambda item: (-_policy_score(item, alert_type, terms), item.id),
        )
        cases = sorted(
            self._repository.list_similar_cases(),
            key=lambda item: (-_case_score(item, terms), item.id),
        )
        return (
            [
                _policy_schema(item, alert_type, terms)
                for item in policies
                if _policy_score(item, alert_type, terms) > 0
            ][:3],
            [
                _case_schema(item, terms)
                for item in cases
                if _case_score(item, terms) > 0
            ][:3],
        )


def _terms(value: str) -> set[str]:
    return set(re.findall(r"[a-z0-9_]+", value.lower()))


def _policy_score(item: PolicySnippet, alert_type: AlertType, terms: set[str]) -> int:
    exact = item.alert_type == alert_type.value
    combined = (
        alert_type == AlertType.COMBINED_OPERATIONAL_REVIEW
        and item.alert_type
        in {AlertType.UNUSUAL_ACTIVITY.value, AlertType.LIQUIDITY_PRESSURE.value}
    )
    overlap = len(_terms(f"{item.title} {item.summary}") & terms)
    return (10 if exact else 7 if combined else 0) + overlap


def _case_score(item: SimilarCaseSummary, terms: set[str]) -> int:
    return len(
        (_terms(f"{item.title} {item.summary}") | {tag.lower() for tag in item.tags})
        & terms
    )


def _policy_schema(
    item: PolicySnippet, alert_type: AlertType, terms: set[str]
) -> RetrievalSource:
    reason = (
        "Exact alert-type policy match."
        if item.alert_type == alert_type.value
        else "Policy matches the combined operational evidence."
    )
    return RetrievalSource(
        source_id=item.id,
        title=item.title,
        excerpt=item.summary,
        relevance_reason=reason,
        permitted_action_categories=item.permitted_action_categories,
    )


def _case_schema(item: SimilarCaseSummary, terms: set[str]) -> RetrievalSource:
    matches = sorted(
        (_terms(f"{item.title} {item.summary}") | {tag.lower() for tag in item.tags})
        & terms
    )
    return RetrievalSource(
        source_id=item.id,
        title=item.title,
        excerpt=item.summary,
        relevance_reason=f"Synthetic sanitized case matches: {', '.join(matches[:4])}.",
        permitted_action_categories=[],
    )
