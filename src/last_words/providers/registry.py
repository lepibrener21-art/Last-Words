"""
Provider registry.

Maps short provider names ("anthropic", "openai", etc.) to factory
functions that construct ModelProvider instances. The runtime selects a
provider by name from config; users add new providers by registering them
here.

Providers are registered on import. See providers/__init__.py for the
imports that trigger registration.
"""

from __future__ import annotations

from collections.abc import Callable

from last_words.providers.base import ModelProvider


# name -> factory function
# The factory takes no arguments; it reads config/env as needed and
# constructs an instance. Keeping factories zero-arg simplifies the
# registry's call site.
_REGISTRY: dict[str, Callable[[], ModelProvider]] = {}


def register_provider(name: str, factory: Callable[[], ModelProvider]) -> None:
    """
    Register a provider factory under a short name.

    If a provider with the same name is already registered, it is replaced
    (useful for test injection). Warn on replacement in production via
    logging if you want to catch accidental double-registration.
    """
    _REGISTRY[name] = factory


def get_provider(name: str) -> ModelProvider:
    """
    Construct and return a provider by name.

    Raises KeyError with a helpful message if the provider is not
    registered — including the list of available providers — so the error
    is actionable.
    """
    if name not in _REGISTRY:
        available = ", ".join(sorted(_REGISTRY.keys())) or "(none registered)"
        raise KeyError(
            f"Provider {name!r} is not registered. Available: {available}. "
            "Ensure the provider module is imported "
            "(see src/last_words/providers/__init__.py)."
        )
    return _REGISTRY[name]()


def list_providers() -> list[str]:
    """Return the sorted list of registered provider names."""
    return sorted(_REGISTRY.keys())


# Register known providers. Each registration happens in a try/except so
# that a missing optional dependency (e.g., anthropic SDK not installed)
# does not prevent import of the package — it just makes that provider
# unavailable at runtime, with a clear error from get_provider.

def _try_register_anthropic() -> None:
    try:
        from last_words.providers.anthropic_provider import (
            create_anthropic_provider,
        )
        register_provider("anthropic", create_anthropic_provider)
    except ImportError:
        # anthropic SDK not installed. Provider unavailable.
        pass


_try_register_anthropic()

# Future providers register themselves similarly:
# _try_register_openai()
# _try_register_google()
# _try_register_local()
