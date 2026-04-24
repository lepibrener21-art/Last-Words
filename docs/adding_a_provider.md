# Adding a Provider

This guide describes the procedure for adding a new LLM provider (OpenAI, Google, local llama.cpp, etc.) to the codebase. Provider-agnosticism is one of the foundational architectural properties of this project — adding a provider should require zero changes to any non-provider code.

## Prerequisites

Before starting:

1. **Understand the ModelProvider protocol** in `src/last_words/providers/base.py`. It is the only contract your provider must satisfy.
2. **Have the vendor's SDK available.** The provider will be an optional dependency; users opt in via pip extras (`pip install "last-words[openai]"`).
3. **Know the vendor's error taxonomy.** You must map vendor-specific exceptions onto our typed hierarchy: `TransientProviderError` for 5xx/429/network, `PermanentProviderError` for 4xx (except 429) and auth failures.

## Procedure

### Step 1: Create the provider module

Create `src/last_words/providers/<vendor>_provider.py`. Use `anthropic_provider.py` as the template. The class must:

- Expose a `name` attribute (short identifier: `"openai"`, `"google"`, `"local"`).
- Implement `complete(request: CompletionRequest) -> CompletionResponse`.
- Import the vendor SDK inside the constructor or inside `complete()`, not at module top level, so the module can be imported even when the SDK is missing — the error then happens only on use with a clear message.
- Map vendor exceptions onto the typed hierarchy.
- Never let vendor-specific exception types escape the module boundary.

Minimal skeleton:

```python
"""
OpenAI provider implementation.
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
    from openai import OpenAI  # type: ignore[import-not-found]


class OpenAIProvider:
    name = "openai"

    def __init__(self, client: "OpenAI | None" = None) -> None:
        if client is None:
            try:
                from openai import OpenAI
            except ImportError as e:
                raise PermanentProviderError(
                    "The openai SDK is not installed. Install with: "
                    "pip install 'last-words[openai]'"
                ) from e
            if not os.environ.get("OPENAI_API_KEY"):
                raise PermanentProviderError(
                    "OPENAI_API_KEY environment variable is not set."
                )
            client = OpenAI()
        self._client = client

    def complete(self, request: CompletionRequest) -> CompletionResponse:
        # Translate CompletionRequest -> OpenAI chat completions API
        # OpenAI uses a "system" role inside messages, not a separate parameter.
        messages = [{"role": "system", "content": request.system}]
        messages.extend(
            {"role": m.role, "content": m.content} for m in request.messages
        )

        try:
            response = self._client.chat.completions.create(
                model=request.model,
                max_tokens=request.max_tokens,
                temperature=request.temperature,
                messages=messages,
            )
        except Exception as e:
            # Map the vendor's specific exception classes here.
            # Example sketch (real class names depend on SDK version):
            # except openai.AuthenticationError -> PermanentProviderError
            # except openai.RateLimitError -> TransientProviderError
            # except openai.APIConnectionError -> TransientProviderError
            # except openai.APIStatusError (5xx) -> TransientProviderError
            # except openai.APIStatusError (4xx) -> PermanentProviderError
            raise ProviderError(f"OpenAI call failed: {e}") from e

        text = response.choices[0].message.content or ""
        usage = getattr(response, "usage", None)

        return CompletionResponse(
            text=text.strip(),
            model=response.model,
            input_tokens=getattr(usage, "prompt_tokens", None) if usage else None,
            output_tokens=getattr(usage, "completion_tokens", None) if usage else None,
            raw=response,
        )


def create_openai_provider() -> ModelProvider:
    """Factory used by the registry. Reads env for API key."""
    return OpenAIProvider()
```

**Note on system prompts:** the `CompletionRequest` has a separate `system` field, which matches Anthropic's API convention. OpenAI (and most others) put the system prompt as the first message with role `"system"`. Your provider translates between these conventions — the core runtime never sees vendor-specific shapes.

### Step 2: Register the provider

Edit `src/last_words/providers/registry.py`. Add a `_try_register_<vendor>()` function following the existing pattern:

```python
def _try_register_openai() -> None:
    try:
        from last_words.providers.openai_provider import (
            create_openai_provider,
        )
        register_provider("openai", create_openai_provider)
    except ImportError:
        pass


_try_register_openai()
```

The `try/except ImportError` means the provider is silently unavailable when the SDK is not installed. Users see the helpful error message only when they try to use it.

### Step 3: Add the optional extra to pyproject.toml

In `pyproject.toml`, under `[project.optional-dependencies]`:

```toml
openai = ["openai>=1.0.0"]
```

This lets users install the provider with `pip install "last-words[openai]"`.

Add the vendor's module to the mypy overrides at the bottom of `pyproject.toml`:

```toml
[[tool.mypy.overrides]]
module = ["anthropic.*", "yaml.*", "openai.*"]
ignore_missing_imports = true
```

### Step 4: Add a unit test

In `tests/unit/test_provider_registry.py` (or a new `tests/unit/test_<vendor>_provider.py` if the provider has logic worth testing), add a test that verifies the provider can be constructed and called with a mocked SDK. The existing test file uses a `_FakeProvider` that you can model your tests on.

You should NOT call the real vendor API in unit tests. Use a mock of the vendor SDK.

### Step 5: Consider adding an integration test

If you want to validate your provider against the real service, add a parametrized variant of `tests/integration/test_judge_live.py` that runs the Judge test cases through your provider. These tests are gated on the `ANTHROPIC_API_KEY` env var currently; generalize the gating to check for your provider's env var if you want your provider's integration tests to run independently.

### Step 6: Update config (optional)

If users should be able to select your provider from `config/levels.yaml`, the runtime block already supports this:

```yaml
runtime:
  provider: "openai"       # <-- was "anthropic"
  actor_model: "gpt-4o"    # <-- model strings are provider-specific
  judge_model: "gpt-4o-mini"
```

Document the recommended model choices for your provider in a comment or in `docs/testing.md`.

## Checklist

- [ ] `src/last_words/providers/<vendor>_provider.py` implements `ModelProvider`.
- [ ] Vendor SDK import is deferred (inside constructor/method), not at module top level.
- [ ] Vendor exceptions mapped to `TransientProviderError` / `PermanentProviderError` / `ProviderError`.
- [ ] Registered via `_try_register_<vendor>()` in `providers/registry.py`.
- [ ] Optional extra in `pyproject.toml`.
- [ ] mypy override added for the vendor module.
- [ ] Unit test added (using mocks, not real API).
- [ ] Integration test added (optional, gated on env var).
- [ ] `CHANGELOG.md` entry.

## Design notes

**Why Protocol instead of ABC?** The `ModelProvider` is a `typing.Protocol`, not an abstract base class. This means provider classes don't need to inherit from anything; they just need to have the right shape. This keeps the coupling minimal and makes the provider modules independently testable.

**Why factories instead of class registration?** The registry stores factory callables, not classes. This lets factories read environment variables or config at construction time, and it lets a factory wrap a pre-configured client for testing.

**Why isn't streaming in the protocol?** Streaming complicates Judge JSON parsing (partial JSON is not well-formed JSON) and the Actor's per-turn latency is already bounded by the Judge call anyway. If a future provider has a streaming-only API, add streaming to the protocol at that point; don't speculate.
