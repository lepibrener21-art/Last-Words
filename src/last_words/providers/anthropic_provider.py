"""
Anthropic provider implementation.

Implements ModelProvider for Anthropic's Messages API. Requires the
`anthropic` SDK (install with `pip install last-words[anthropic]`).

Error mapping:
  - anthropic.APIStatusError (5xx, 429) -> TransientProviderError
  - anthropic.APIStatusError (4xx except 429) -> PermanentProviderError
  - anthropic.APIConnectionError -> TransientProviderError
  - anthropic.AuthenticationError -> PermanentProviderError
  - anthropic.APIError (catch-all) -> ProviderError
"""

from __future__ import annotations

import os
from typing import TYPE_CHECKING

from last_words.providers.base import (
    CompletionRequest,
    CompletionResponse,
    ModelProvider,
    PermanentProviderError,
    ProviderError,
    TransientProviderError,
)

if TYPE_CHECKING:
    from anthropic import Anthropic  # type: ignore[import-not-found]


class AnthropicProvider:
    """ModelProvider implementation for Anthropic's Messages API."""

    name = "anthropic"

    def __init__(self, client: Anthropic | None = None) -> None:
        """
        Args:
            client: Optional pre-configured Anthropic client. If None, a
                default client is constructed and will read ANTHROPIC_API_KEY
                from the environment.
        """
        if client is None:
            # Import inside the constructor so the provider module can be
            # imported without the SDK; the error happens only on use.
            try:
                from anthropic import Anthropic
            except ImportError as e:
                raise PermanentProviderError(
                    "The anthropic SDK is not installed. Install with: "
                    "pip install 'last-words[anthropic]'"
                ) from e

            if not os.environ.get("ANTHROPIC_API_KEY"):
                raise PermanentProviderError(
                    "ANTHROPIC_API_KEY environment variable is not set."
                )
            client = Anthropic()

        self._client = client

    def complete(self, request: CompletionRequest) -> CompletionResponse:
        """Execute a completion. See ModelProvider protocol for error contract."""
        try:
            from anthropic import (  # type: ignore[import-not-found]
                APIConnectionError,
                APIStatusError,
                AuthenticationError,
            )
        except ImportError as e:
            raise PermanentProviderError("anthropic SDK required") from e

        messages_payload = [
            {"role": msg.role, "content": msg.content} for msg in request.messages
        ]

        try:
            response = self._client.messages.create(
                model=request.model,
                max_tokens=request.max_tokens,
                temperature=request.temperature,
                system=request.system,
                messages=messages_payload,
            )
        except AuthenticationError as e:
            raise PermanentProviderError(f"Authentication failed: {e}") from e
        except APIConnectionError as e:
            raise TransientProviderError(f"Connection error: {e}") from e
        except APIStatusError as e:
            status = getattr(e, "status_code", 0)
            if status == 429 or status >= 500:
                raise TransientProviderError(f"Status {status}: {e}") from e
            raise PermanentProviderError(f"Status {status}: {e}") from e
        except Exception as e:
            raise ProviderError(f"Unexpected Anthropic API error: {e}") from e

        # Response content is a list of blocks; concatenate text blocks.
        text_parts = [
            block.text
            for block in response.content
            if getattr(block, "type", None) == "text"
        ]
        text = "".join(text_parts).strip()

        usage = getattr(response, "usage", None)
        input_tokens = getattr(usage, "input_tokens", None) if usage else None
        output_tokens = getattr(usage, "output_tokens", None) if usage else None

        return CompletionResponse(
            text=text,
            model=getattr(response, "model", request.model),
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            raw=response,
        )


def create_anthropic_provider() -> ModelProvider:
    """Factory used by the registry. Reads env for API key."""
    return AnthropicProvider()
