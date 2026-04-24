"""Unit tests for the provider registry."""

from __future__ import annotations

import pytest

from last_words.providers.base import (
    CompletionRequest,
    CompletionResponse,
    ModelProvider,
)
from last_words.providers.registry import (
    get_provider,
    list_providers,
    register_provider,
)


class _FakeProvider:
    name = "fake"

    def complete(self, request: CompletionRequest) -> CompletionResponse:
        return CompletionResponse(
            text=f"fake response to {request.model}",
            model=request.model,
            input_tokens=1,
            output_tokens=1,
        )


def test_register_and_get() -> None:
    register_provider("fake", _FakeProvider)
    provider = get_provider("fake")
    assert isinstance(provider, _FakeProvider)  # type: ignore[arg-type]

    # list_providers includes our registration.
    assert "fake" in list_providers()


def test_get_unknown_raises_keyerror_with_helpful_message() -> None:
    with pytest.raises(KeyError, match="not registered"):
        get_provider("definitely-not-a-real-provider")


def test_registered_provider_is_usable() -> None:
    register_provider("fake2", _FakeProvider)
    provider = get_provider("fake2")
    request = CompletionRequest(
        model="test-model",
        system="system",
        messages=(),
    )
    response = provider.complete(request)
    assert response.text == "fake response to test-model"
    assert response.model == "test-model"


def test_provider_implements_protocol() -> None:
    """The Protocol check is duck-typed; this is a reminder test."""
    provider = _FakeProvider()
    # If this function signature were wrong, mypy would catch it in CI.
    # Runtime check is minimal because Protocol is structural.
    _: ModelProvider = provider
    assert provider.name == "fake"
