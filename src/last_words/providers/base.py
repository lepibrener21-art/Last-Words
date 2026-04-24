"""
Provider abstraction.

Defines the Protocol that any LLM provider must implement to be usable
by the game runtime. The rest of the codebase talks to providers through
this interface and nothing else.

Design principles:
  - Vendor-neutral request and response shapes.
  - No streaming in the abstraction; add if a future provider benefits
    from it, but streaming complicates Judge JSON parsing so we avoid
    it by default.
  - Errors raise typed exceptions so retry logic can distinguish
    transient failures from permanent ones.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal, Protocol


# A single message in a conversation. Role values mirror the Anthropic and
# OpenAI conventions.
Role = Literal["user", "assistant"]


@dataclass(frozen=True)
class Message:
    """A single conversational turn."""

    role: Role
    content: str


@dataclass(frozen=True)
class CompletionRequest:
    """
    A provider-neutral completion request.

    All fields a provider might reasonably need. Providers should ignore
    fields they do not support rather than error; log a warning if a
    dropped field would have changed behavior.
    """

    model: str
    system: str
    messages: tuple[Message, ...]
    max_tokens: int = 512
    temperature: float = 0.7
    # Additional provider-specific hints, ignored by providers that do not
    # recognize them. Use sparingly.
    extra: dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class CompletionResponse:
    """A provider-neutral completion response."""

    text: str
    model: str                 # the model actually used (may differ from request)
    input_tokens: int | None   # None if the provider does not report
    output_tokens: int | None
    raw: object | None = None  # opaque provider-specific object for debugging


class ProviderError(Exception):
    """Base class for all provider errors."""


class TransientProviderError(ProviderError):
    """Errors that may succeed on retry (rate limits, transient network, 5xx)."""


class PermanentProviderError(ProviderError):
    """Errors that will not succeed on retry (auth, invalid request, 4xx except 429)."""


class ModelProvider(Protocol):
    """
    The abstraction over LLM vendors.

    Implementations live in sibling modules (anthropic_provider.py,
    openai_provider.py, etc.) and register themselves via
    last_words.providers.registry.register_provider.

    Implementations must:
      - Raise TransientProviderError for 5xx, 429, and network errors.
      - Raise PermanentProviderError for 4xx (except 429) and config errors.
      - Never raise vendor-specific exceptions beyond their module boundary.
    """

    @property
    def name(self) -> str:
        """Short identifier (e.g., 'anthropic', 'openai', 'local')."""
        ...

    def complete(self, request: CompletionRequest) -> CompletionResponse:
        """Synchronous completion. Raises ProviderError subclasses on failure."""
        ...
