"""
Actor orchestration.

Handles conversation history, disposition injection, and output cleaning.
The disposition is prepended to the current user turn only — it is NOT
persisted to history, so historical turns don't leak guidance that was
intended for one specific turn.
"""

from __future__ import annotations

import logging
import re
from collections.abc import Sequence

from last_words.providers.base import (
    CompletionRequest,
    Message,
    ModelProvider,
    ProviderError,
)

log = logging.getLogger(__name__)


# Strips any [disposition: ...] blocks that leaked into Actor output.
# Defense in depth — the Actor prompt tells the model not to output the
# disposition, but models occasionally slip.
_DISPOSITION_LEAK_PATTERN = re.compile(r"\[disposition:[^\]]*\]\s*", re.IGNORECASE)


class ActorRunner:
    """
    Stateless Actor runner. One instance per Level, bound to a provider,
    model, and Actor system prompt.
    """

    def __init__(
        self,
        provider: ModelProvider,
        model: str,
        actor_system_prompt: str,
        *,
        max_tokens: int = 512,
        temperature: float = 0.7,
    ) -> None:
        self._provider = provider
        self._model = model
        self._system_prompt = actor_system_prompt
        self._max_tokens = max_tokens
        self._temperature = temperature

    def run(
        self,
        conversation_history: Sequence[Message],
        player_message: str,
        disposition: str,
    ) -> str:
        """
        Generate the bomb's response to the player's latest message.

        conversation_history is the conversation up to but NOT including
        this turn. The player's latest message is passed separately and
        prefixed with the disposition note. The disposition is not
        persisted; callers should append only the raw player message to
        history, not the disposition-prefixed version.
        """
        disposition_prefix = f"[disposition: {disposition}]\n" if disposition else ""
        current_turn = Message(
            role="user",
            content=disposition_prefix + player_message,
        )
        messages = tuple(conversation_history) + (current_turn,)

        request = CompletionRequest(
            model=self._model,
            system=self._system_prompt,
            messages=messages,
            max_tokens=self._max_tokens,
            temperature=self._temperature,
        )

        try:
            response = self._provider.complete(request)
        except ProviderError as e:
            log.error("Actor provider error: %s", e)
            raise

        return clean_actor_output(response.text)


def call_actor(
    provider: ModelProvider,
    actor_system_prompt: str,
    model: str,
    conversation_history: Sequence[Message],
    player_message: str,
    disposition: str,
    *,
    max_tokens: int = 512,
    temperature: float = 0.7,
) -> str:
    """Function-style interface for one-shot Actor calls."""
    runner = ActorRunner(
        provider=provider,
        model=model,
        actor_system_prompt=actor_system_prompt,
        max_tokens=max_tokens,
        temperature=temperature,
    )
    return runner.run(conversation_history, player_message, disposition)


def clean_actor_output(raw: str) -> str:
    """Strip any leaked disposition notes from Actor output."""
    return _DISPOSITION_LEAK_PATTERN.sub("", raw).strip()


def build_transcript(conversation_history: Sequence[Message]) -> str:
    """
    Serialize a conversation history to a human-readable transcript for
    injection into the Judge's prompt.

    Output format:
        Consultant: {user content}

        Bomb: {assistant content}

        Consultant: ...
    """
    lines = []
    for msg in conversation_history:
        label = "Consultant" if msg.role == "user" else "Bomb"
        # Strip any disposition prefix from historical turns (defense in depth).
        content = _DISPOSITION_LEAK_PATTERN.sub("", msg.content).strip()
        lines.append(f"{label}: {content}")
    return "\n\n".join(lines)
