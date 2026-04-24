"""
LLM provider abstraction.

The game's runtime never imports a vendor SDK directly. It interacts with
LLMs through the ModelProvider protocol defined in base.py. Each vendor
(Anthropic, OpenAI, local models, etc.) gets its own module implementing
the protocol.

Adding a new provider requires:
  1. A module here implementing ModelProvider.
  2. Registration in the providers registry.
  3. An optional extra in pyproject.toml for the vendor SDK dependency.

See docs/adding_a_provider.md for the full procedure.
"""

from last_words.providers.base import (
    CompletionRequest,
    CompletionResponse,
    Message,
    ModelProvider,
    ProviderError,
    TransientProviderError,
)
from last_words.providers.registry import (
    get_provider,
    register_provider,
    list_providers,
)

__all__ = [
    "CompletionRequest",
    "CompletionResponse",
    "Message",
    "ModelProvider",
    "ProviderError",
    "TransientProviderError",
    "get_provider",
    "register_provider",
    "list_providers",
]
