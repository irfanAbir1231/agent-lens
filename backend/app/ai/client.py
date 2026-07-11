from __future__ import annotations

from typing import Any, Protocol

from openai import OpenAI

from app.ai.config import AIConfig
from app.schemas.advisory import AIAdvisory


class AdvisoryClient(Protocol):
    def parse_advisory(self, *, model: str, payload: str) -> AIAdvisory: ...


class OpenAIAdvisoryClient:
    def __init__(self, config: AIConfig) -> None:
        if not config.api_key:
            raise ValueError("OPENAI_API_KEY is not configured.")
        self._client = OpenAI(
            api_key=config.api_key,
            timeout=config.timeout_seconds,
            max_retries=0,
        )

    def parse_advisory(self, *, model: str, payload: str) -> AIAdvisory:
        from app.ai.prompts.advisory import ADVISORY_PROMPT
        from app.ai.prompts.system import SYSTEM_PROMPT

        response: Any = self._client.responses.parse(
            model=model,
            input=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": f"{ADVISORY_PROMPT}\n\nSanitized context:\n{payload}",
                },
            ],
            text_format=AIAdvisory,
            store=False,
        )
        for output in response.output:
            if getattr(output, "type", None) != "message":
                continue
            for content in output.content:
                if getattr(content, "type", None) == "refusal":
                    raise AdvisoryRefusalError(
                        "The model refused the advisory request."
                    )
        if response.output_parsed is None:
            raise MissingParsedOutputError("Structured advisory output was missing.")
        return AIAdvisory.model_validate(response.output_parsed)


class AdvisoryRefusalError(RuntimeError):
    pass


class MissingParsedOutputError(RuntimeError):
    pass
