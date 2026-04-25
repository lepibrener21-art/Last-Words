"""Unit tests for the Ollama provider.

All tests mock the HTTP layer — no real Ollama server is required.
"""

from __future__ import annotations

import json
from io import BytesIO
from typing import Any
from unittest.mock import MagicMock, patch
from urllib.error import HTTPError, URLError

import pytest

from last_words.providers.base import (
    CompletionRequest,
    Message,
)
from last_words.providers.ollama_provider import OllamaProvider
from last_words.providers.base import (
    PermanentProviderError,
    TransientProviderError,
    ProviderError,
)


# ── Helpers ──────────────────────────────────────────────────────────────────

def _make_request(
    model: str = "llama3.2:3b",
    system: str = "You are a bomb.",
    messages: tuple[Message, ...] = (Message(role="user", content="Hello"),),
    temperature: float = 0.7,
    max_tokens: int = 256,
) -> CompletionRequest:
    return CompletionRequest(
        model=model,
        system=system,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
    )


def _ollama_response(
    content: str = "Tick tock.",
    model: str = "llama3.2:3b",
    prompt_eval_count: int = 42,
    eval_count: int = 10,
) -> bytes:
    """Build a minimal Ollama /api/chat non-streaming response body."""
    return json.dumps({
        "model": model,
        "message": {"role": "assistant", "content": content},
        "prompt_eval_count": prompt_eval_count,
        "eval_count": eval_count,
        "done": True,
    }).encode("utf-8")


def _mock_urlopen(body: bytes, status: int = 200) -> MagicMock:
    """Return a context-manager mock that yields a response-like object."""
    resp = MagicMock()
    resp.read.return_value = body
    resp.__enter__ = lambda s: s
    resp.__exit__ = MagicMock(return_value=False)
    return resp


# ── Constructor tests ─────────────────────────────────────────────────────────

def test_default_base_url() -> None:
    provider = OllamaProvider()
    assert provider.base_url == "http://localhost:11434"


def test_custom_base_url_strips_trailing_slash() -> None:
    provider = OllamaProvider(base_url="http://192.168.1.5:11434/")
    assert provider.base_url == "http://192.168.1.5:11434"


def test_base_url_from_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("OLLAMA_BASE_URL", "http://remotehost:11434")
    provider = OllamaProvider()
    assert provider.base_url == "http://remotehost:11434"


def test_explicit_base_url_overrides_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("OLLAMA_BASE_URL", "http://remotehost:11434")
    provider = OllamaProvider(base_url="http://localhost:11434")
    assert provider.base_url == "http://localhost:11434"


def test_name_attribute() -> None:
    assert OllamaProvider.name == "ollama"


# ── Successful completion ─────────────────────────────────────────────────────

def test_complete_returns_correct_text() -> None:
    provider = OllamaProvider()
    mock_resp = _mock_urlopen(_ollama_response(content="  Tick tock.  "))

    with patch("last_words.providers.ollama_provider.urlopen", return_value=mock_resp):
        result = provider.complete(_make_request())

    assert result.text == "Tick tock."


def test_complete_returns_token_counts() -> None:
    provider = OllamaProvider()
    mock_resp = _mock_urlopen(
        _ollama_response(prompt_eval_count=77, eval_count=13)
    )

    with patch("last_words.providers.ollama_provider.urlopen", return_value=mock_resp):
        result = provider.complete(_make_request())

    assert result.input_tokens == 77
    assert result.output_tokens == 13


def test_complete_returns_model_from_response() -> None:
    provider = OllamaProvider()
    mock_resp = _mock_urlopen(_ollama_response(model="qwen2.5:3b"))

    with patch("last_words.providers.ollama_provider.urlopen", return_value=mock_resp):
        result = provider.complete(_make_request(model="qwen2.5:3b"))

    assert result.model == "qwen2.5:3b"


def test_complete_raw_is_parsed_dict() -> None:
    provider = OllamaProvider()
    mock_resp = _mock_urlopen(_ollama_response())

    with patch("last_words.providers.ollama_provider.urlopen", return_value=mock_resp):
        result = provider.complete(_make_request())

    assert isinstance(result.raw, dict)
    assert "message" in result.raw  # type: ignore[operator]


# ── Request payload shape ─────────────────────────────────────────────────────

def test_system_prompt_becomes_first_message() -> None:
    """Ollama expects system as role=system in messages, not a separate field."""
    provider = OllamaProvider()
    captured: list[dict[str, Any]] = []

    def fake_urlopen(req: Any, timeout: Any) -> Any:
        body = json.loads(req.data.decode("utf-8"))
        captured.append(body)
        return _mock_urlopen(_ollama_response())

    with patch("last_words.providers.ollama_provider.urlopen", side_effect=fake_urlopen):
        provider.complete(_make_request(system="Be a bomb."))

    assert captured[0]["messages"][0] == {"role": "system", "content": "Be a bomb."}


def test_player_message_appended_after_system() -> None:
    provider = OllamaProvider()
    captured: list[dict[str, Any]] = []

    def fake_urlopen(req: Any, timeout: Any) -> Any:
        captured.append(json.loads(req.data.decode("utf-8")))
        return _mock_urlopen(_ollama_response())

    request = _make_request(
        messages=(Message(role="user", content="Are you okay?"),)
    )
    with patch("last_words.providers.ollama_provider.urlopen", side_effect=fake_urlopen):
        provider.complete(request)

    messages = captured[0]["messages"]
    assert messages[1] == {"role": "user", "content": "Are you okay?"}


def test_stream_is_false_in_payload() -> None:
    provider = OllamaProvider()
    captured: list[dict[str, Any]] = []

    def fake_urlopen(req: Any, timeout: Any) -> Any:
        captured.append(json.loads(req.data.decode("utf-8")))
        return _mock_urlopen(_ollama_response())

    with patch("last_words.providers.ollama_provider.urlopen", side_effect=fake_urlopen):
        provider.complete(_make_request())

    assert captured[0]["stream"] is False


def test_temperature_and_num_predict_in_options() -> None:
    provider = OllamaProvider()
    captured: list[dict[str, Any]] = []

    def fake_urlopen(req: Any, timeout: Any) -> Any:
        captured.append(json.loads(req.data.decode("utf-8")))
        return _mock_urlopen(_ollama_response())

    with patch("last_words.providers.ollama_provider.urlopen", side_effect=fake_urlopen):
        provider.complete(_make_request(temperature=0.0, max_tokens=256))

    options = captured[0]["options"]
    assert options["temperature"] == 0.0
    assert options["num_predict"] == 256


# ── Error mapping ─────────────────────────────────────────────────────────────

def _http_error(status: int, body: bytes = b'{"error": "boom"}') -> HTTPError:
    return HTTPError(
        url="http://localhost:11434/api/chat",
        code=status,
        msg=f"HTTP {status}",
        hdrs=MagicMock(),  # type: ignore[arg-type]
        fp=BytesIO(body),
    )


def test_404_raises_permanent_with_pull_hint() -> None:
    provider = OllamaProvider()
    with patch(
        "last_words.providers.ollama_provider.urlopen",
        side_effect=_http_error(404),
    ):
        with pytest.raises(PermanentProviderError, match="ollama pull"):
            provider.complete(_make_request(model="nonexistent:latest"))


def test_500_raises_transient() -> None:
    provider = OllamaProvider()
    with patch(
        "last_words.providers.ollama_provider.urlopen",
        side_effect=_http_error(500),
    ):
        with pytest.raises(TransientProviderError):
            provider.complete(_make_request())


def test_429_raises_transient() -> None:
    provider = OllamaProvider()
    with patch(
        "last_words.providers.ollama_provider.urlopen",
        side_effect=_http_error(429),
    ):
        with pytest.raises(TransientProviderError):
            provider.complete(_make_request())


def test_400_raises_permanent() -> None:
    provider = OllamaProvider()
    with patch(
        "last_words.providers.ollama_provider.urlopen",
        side_effect=_http_error(400),
    ):
        with pytest.raises(PermanentProviderError):
            provider.complete(_make_request())


def test_url_error_raises_transient_with_serve_hint() -> None:
    provider = OllamaProvider()
    with patch(
        "last_words.providers.ollama_provider.urlopen",
        side_effect=URLError("Connection refused"),
    ):
        with pytest.raises(TransientProviderError, match="ollama serve"):
            provider.complete(_make_request())


def test_unexpected_exception_raises_provider_error() -> None:
    provider = OllamaProvider()
    with patch(
        "last_words.providers.ollama_provider.urlopen",
        side_effect=RuntimeError("disk full"),
    ):
        with pytest.raises(ProviderError):
            provider.complete(_make_request())


# ── Registry integration ──────────────────────────────────────────────────────

def test_ollama_registered_in_registry() -> None:
    from last_words.providers.registry import list_providers
    assert "ollama" in list_providers()


def test_ollama_factory_returns_provider_instance() -> None:
    from last_words.providers.registry import get_provider
    provider = get_provider("ollama")
    assert provider.name == "ollama"  # type: ignore[union-attr]
