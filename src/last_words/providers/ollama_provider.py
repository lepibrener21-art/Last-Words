"""
Ollama provider implementation.

Calls the Ollama local inference server via its HTTP REST API.
No third-party SDK required — uses only the Python standard library.

The Ollama server exposes an OpenAI-compatible /api/chat endpoint.
System prompts are injected as the first message with role "system",
matching Ollama's convention (and OpenAI's), rather than as a separate
top-level parameter (Anthropic's convention).

Error mapping:
  - Connection refused / network error  -> TransientProviderError
    (Ollama process not running; fix: `ollama serve`)
  - HTTP 5xx                            -> TransientProviderError
  - HTTP 404 — model not pulled         -> PermanentProviderError
  - HTTP 4xx (other)                    -> PermanentProviderError

Configuration:
  - OLLAMA_BASE_URL env var sets the server address
    (default: http://localhost:11434)
  - Model names are whatever you pass in CompletionRequest.model,
    matching the tag you pulled with `ollama pull <model>`.
"""

from __future__ import annotations

import json
import os
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from last_words.providers.base import (
    CompletionRequest,
    CompletionResponse,
    ModelProvider,
    PermanentProviderError,
    ProviderError,
    TransientProviderError,
)

_DEFAULT_BASE_URL = "http://localhost:11434"
_CHAT_PATH = "/api/chat"
# Generous timeout: local models on CPU can be slow on first token.
_TIMEOUT_SECONDS = 300


class OllamaProvider:
    """ModelProvider implementation for the Ollama local inference server."""

    name = "ollama"

    def __init__(self, base_url: str | None = None) -> None:
        """
        Args:
            base_url: Ollama server root URL. If None, reads OLLAMA_BASE_URL
                from the environment, defaulting to http://localhost:11434.
        """
        self._base_url = (
            base_url or os.environ.get("OLLAMA_BASE_URL", _DEFAULT_BASE_URL)
        ).rstrip("/")

    @property
    def base_url(self) -> str:
        return self._base_url

    def complete(self, request: CompletionRequest) -> CompletionResponse:
        """Call Ollama's /api/chat endpoint synchronously."""
        # Ollama (like OpenAI) takes the system prompt as a role="system"
        # message, not as a separate top-level field.
        messages: list[dict[str, str]] = [
            {"role": "system", "content": request.system}
        ]
        messages.extend(
            {"role": msg.role, "content": msg.content} for msg in request.messages
        )

        payload: dict[str, Any] = {
            "model": request.model,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": request.temperature,
                # Ollama calls max_tokens "num_predict".
                "num_predict": request.max_tokens,
            },
        }

        body = json.dumps(payload).encode("utf-8")
        req = Request(
            f"{self._base_url}{_CHAT_PATH}",
            data=body,
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        try:
            with urlopen(req, timeout=_TIMEOUT_SECONDS) as resp:
                data: dict[str, Any] = json.loads(resp.read().decode("utf-8"))
        except HTTPError as e:
            status = e.code
            if status == 404:
                raise PermanentProviderError(
                    f"Model {request.model!r} not found on Ollama. "
                    f"Pull it first:  ollama pull {request.model}"
                ) from e
            if status == 429 or status >= 500:
                raise TransientProviderError(
                    f"Ollama server error {status}. Retry or check server logs."
                ) from e
            try:
                detail = json.loads(e.read().decode("utf-8")).get("error", "")
            except Exception:
                detail = str(e.reason)
            raise PermanentProviderError(
                f"Ollama HTTP {status}: {detail}"
            ) from e
        except URLError as e:
            raise TransientProviderError(
                f"Cannot connect to Ollama at {self._base_url}. "
                "Is the server running?  Start it with:  ollama serve"
            ) from e
        except Exception as e:
            raise ProviderError(f"Unexpected Ollama error: {e}") from e

        text: str = data.get("message", {}).get("content", "").strip()
        model_used: str = data.get("model", request.model)
        # Ollama reports token counts as prompt_eval_count / eval_count.
        input_tokens: int | None = data.get("prompt_eval_count")
        output_tokens: int | None = data.get("eval_count")

        return CompletionResponse(
            text=text,
            model=model_used,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            raw=data,
        )


def create_ollama_provider() -> ModelProvider:
    """Factory used by the registry. Reads OLLAMA_BASE_URL from env if set."""
    return OllamaProvider()
