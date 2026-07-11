from __future__ import annotations

from app.ai.schemas import SanitizedAdvisoryInput
from app.schemas.advisory import (
    AdvisoryAction,
    AdvisorySourceReference,
    AIAdvisory,
)
from app.schemas.enums import UserRole


def deterministic_fallback(payload: SanitizedAdvisoryInput) -> AIAdvisory:
    primary = payload.providers[0]
    action_category = (
        primary.allowed_actions[0] if primary.allowed_actions else "manual_verification"
    )
    sources = [
        source.source_id
        for context in payload.providers
        for source in context.policy_sources + context.similar_cases
    ]
    source_ids = list(dict.fromkeys(sources))
    return AIAdvisory(
        summary=(
            "Generated guidance is unavailable; deterministic review remains available."
        ),
        operational_assessment=(
            "Review the provider-specific deterministic evidence and limitations "
            "before taking any operational action."
        ),
        why=[
            f"{context.provider}: {context.severity} deterministic review."
            for context in payload.providers
        ],
        recommended_actions=[
            AdvisoryAction(
                rank=1,
                title="Perform the permitted manual review",
                rationale=(
                    "Verify the supplied evidence and uncertainty with a human "
                    "reviewer."
                ),
                action_category=action_category,
                provider=primary.provider,
                responsible_role=primary.required_human_role,
                source_ids=source_ids[:3],
            )
        ],
        responsible_role=primary.required_human_role,
        source_ids=source_ids,
        uncertainty=[
            *primary.limitations,
            "Generated advisory guidance is unavailable.",
        ],
        human_verification_questions=[
            "Does current provider-side evidence confirm the deterministic concern?"
        ],
        source_references=[
            AdvisorySourceReference(
                source_id=source_id,
                relevance="Supplied deterministic policy or sanitized case context.",
            )
            for source_id in source_ids
        ],
    )


def no_advisory_guidance(*, reason: str) -> AIAdvisory:
    return AIAdvisory(
        summary=reason,
        operational_assessment=(
            "Deterministic provider evidence remains available for human review."
        ),
        why=[reason],
        recommended_actions=[
            AdvisoryAction(
                rank=1,
                title="Continue deterministic monitoring",
                rationale="No generated advisory is required for this analysis.",
                action_category="continue_monitoring",
                responsible_role=UserRole.RISK_ANALYST,
                source_ids=[],
            )
        ],
        responsible_role=UserRole.RISK_ANALYST,
        source_ids=[],
        uncertainty=["No generated advisory was requested."],
        human_verification_questions=[],
        source_references=[],
    )
