from __future__ import annotations

from app.ai.schemas import SanitizedAdvisoryInput
from app.schemas.advisory import AIAdvisory
from app.schemas.enums import Provider, UserRole


def validate_advisory_output(
    advisory: AIAdvisory, supplied: SanitizedAdvisoryInput
) -> None:
    source_ids = {
        source.source_id
        for context in supplied.providers
        for source in context.policy_sources + context.similar_cases
    }
    allowed_actions = {
        action for context in supplied.providers for action in context.allowed_actions
    }
    allowed_roles = {
        UserRole(context.required_human_role) for context in supplied.providers
    }
    allowed_providers = {Provider(context.provider) for context in supplied.providers}
    ranks = [item.rank for item in advisory.recommended_actions]
    if ranks != list(range(1, len(ranks) + 1)):
        raise InvalidAdvisoryOutputError(
            "Recommended action ranks must be unique, ordered, and contiguous."
        )
    if not advisory.recommended_actions:
        raise InvalidAdvisoryOutputError("At least one safe action is required.")
    if UserRole(advisory.responsible_role) not in allowed_roles:
        raise InvalidAdvisoryOutputError("The responsible role was not supplied.")
    if not set(advisory.source_ids).issubset(source_ids):
        raise InvalidAdvisoryOutputError("The advisory cited an unknown source.")
    if source_ids and not advisory.source_ids:
        raise InvalidAdvisoryOutputError("The advisory omitted supplied sources.")
    for reference in advisory.source_references:
        if reference.source_id not in source_ids:
            raise InvalidAdvisoryOutputError("A source reference was not supplied.")
    for action in advisory.recommended_actions:
        if source_ids and not action.source_ids:
            raise InvalidAdvisoryOutputError("An action omitted source support.")
        if action.action_category not in allowed_actions:
            raise InvalidAdvisoryOutputError("An action was outside the allowlist.")
        if UserRole(action.responsible_role) not in allowed_roles:
            raise InvalidAdvisoryOutputError("An action used an unsupported role.")
        if (
            action.provider is not None
            and Provider(action.provider) not in allowed_providers
        ):
            raise InvalidAdvisoryOutputError("An action used an excluded provider.")
        if not set(action.source_ids).issubset(source_ids):
            raise InvalidAdvisoryOutputError("An action cited an unknown source.")


class InvalidAdvisoryOutputError(ValueError):
    pass
