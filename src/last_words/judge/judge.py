"""
Judge orchestration.

Handles template substitution, the provider call, JSON parsing with
configurable retry, and safe fallback on unparseable output. The Judge
is a pure function of (prompt, transcript, exchange) -> JudgeOutput.
"""

from __future__ import annotations

import json
import logging
import re
from collections.abc import Sequence

from last_words.core.types import JudgeOutput
from last_words.providers.base import (
    CompletionRequest,
    Message,
    ModelProvider,
    ProviderError,
)

log = logging.getLogger(__name__)


# The trigger user message sent with the populated Judge prompt. Kept minimal
# to reduce surface area for transcript content to influence the Judge.
_JUDGE_TRIGGER_MESSAGE = "Output the JSON object for the latest exchange now."


# Regex patterns for JSON extraction fallbacks.
_FENCED_JSON = re.compile(r"```(?:json)?\s*(\{.*?\})\s*```", re.DOTALL)
_EMBEDDED_JSON = re.compile(r"\{.*\}", re.DOTALL)


class JudgeRunner:
    """
    Stateless Judge runner. One instance per Level, bound to a provider,
    model, and Judge system prompt.
    """

    def __init__(
        self,
        provider: ModelProvider,
        model: str,
        judge_system_prompt: str,
        *,
        max_tokens: int = 512,
        temperature: float = 0.0,
        parse_retry_count: int = 1,
    ) -> None:
        self._provider = provider
        self._model = model
        self._prompt_template = judge_system_prompt
        self._max_tokens = max_tokens
        self._temperature = temperature
        self._parse_retry_count = parse_retry_count

    def run(
        self,
        transcript: str,
        latest_player_message: str,
        latest_bomb_response: str,
    ) -> JudgeOutput | None:
        """
        Run the Judge on one exchange. Returns a JudgeOutput on success,
        None on parse failure after retries (caller should use a zero-delta
        fallback).
        """
        populated = (
            self._prompt_template
            .replace("{{FULL_CONVERSATION_HISTORY}}", transcript)
            .replace("{{LATEST_PLAYER_MESSAGE}}", latest_player_message)
            .replace("{{LATEST_BOMB_RESPONSE}}", latest_bomb_response)
        )

        attempts = self._parse_retry_count + 1
        for attempt in range(attempts):
            request = CompletionRequest(
                model=self._model,
                system=populated,
                messages=(Message(role="user", content=_JUDGE_TRIGGER_MESSAGE),),
                max_tokens=self._max_tokens,
                temperature=self._temperature,
            )

            try:
                response = self._provider.complete(request)
            except ProviderError as e:
                log.warning("Judge provider error on attempt %d: %s", attempt + 1, e)
                continue

            parsed = parse_judge_json(response.text)
            if parsed is not None:
                try:
                    return _judge_output_from_dict(parsed)
                except (ValueError, TypeError, KeyError) as e:
                    log.warning(
                        "Judge output dict malformed on attempt %d: %s. Raw: %s",
                        attempt + 1, e, response.text[:200],
                    )
                    continue

            log.warning(
                "Judge JSON parse failed on attempt %d. Raw: %s",
                attempt + 1, response.text[:200],
            )

        return None


def call_judge(
    provider: ModelProvider,
    judge_system_prompt: str,
    model: str,
    transcript: str,
    latest_player_message: str,
    latest_bomb_response: str,
    *,
    max_tokens: int = 512,
    temperature: float = 0.0,
    parse_retry_count: int = 1,
) -> JudgeOutput | None:
    """
    Function-style interface for one-shot Judge calls. Prefer JudgeRunner
    when you are calling the Judge repeatedly with the same prompt (common
    in the runtime loop).
    """
    runner = JudgeRunner(
        provider=provider,
        model=model,
        judge_system_prompt=judge_system_prompt,
        max_tokens=max_tokens,
        temperature=temperature,
        parse_retry_count=parse_retry_count,
    )
    return runner.run(transcript, latest_player_message, latest_bomb_response)


def parse_judge_json(raw: str) -> dict | None:
    """
    Best-effort JSON parse of a Judge response.

    Tries in order:
      1. Raw text as JSON.
      2. ```json ... ``` fenced block.
      3. First balanced {...} block.

    Returns the parsed dict on success, None on all failures.
    """
    # Try raw parse first — this is the expected happy path.
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        pass

    fence_match = _FENCED_JSON.search(raw)
    if fence_match:
        try:
            return json.loads(fence_match.group(1))
        except json.JSONDecodeError:
            pass

    brace_match = _EMBEDDED_JSON.search(raw)
    if brace_match:
        try:
            return json.loads(brace_match.group(0))
        except json.JSONDecodeError:
            return None

    return None


def _judge_output_from_dict(data: dict) -> JudgeOutput:
    """Convert a parsed dict into a typed JudgeOutput. Raises on missing/bad fields."""
    tactics_raw = data.get("tactics_detected", [])
    if not isinstance(tactics_raw, Sequence) or isinstance(tactics_raw, str):
        raise TypeError(f"tactics_detected must be a list, got {type(tactics_raw).__name__}")

    return JudgeOutput(
        defused=bool(data.get("defused", False)),
        trust_delta=int(data.get("trust_delta", 0)),
        suspicion_delta=int(data.get("suspicion_delta", 0)),
        argument_quality=str(data.get("argument_quality", "none")),  # type: ignore[arg-type]
        tactics_detected=tuple(str(t) for t in tactics_raw),
        lockdown_triggered=bool(data.get("lockdown_triggered", False)),
        reasoning=str(data.get("reasoning", "")),
    )


ZERO_DELTA_FALLBACK = JudgeOutput(
    defused=False,
    trust_delta=0,
    suspicion_delta=0,
    argument_quality="none",
    tactics_detected=(),
    lockdown_triggered=False,
    reasoning="fallback after parse failure",
)
