"""
Last Words — a conversational puzzle game where the player talks a
sentient AI bomb out of detonating.

The package is organized into subpackages by responsibility:

- core      Pure game logic. State, dispositions, Judge output types.
            No I/O, no model calls. Unit-testable without mocks.
- providers LLM provider abstraction. ModelProvider protocol and
            concrete implementations (Anthropic, others).
- levels    Per-level modules. Each level is self-contained.
- judge     Judge-specific logic: prompt substitution, parsing, retry.
- actor     Actor-specific logic: conversation management, disposition injection.
- runtime   Orchestration. The play loop lives here.
- ui        Presentation. Terminal renderer and other UI implementations.

Canonical design lives in the design/ directory at the project root.
This package implements that design. Any conflict between code and
design/level_design.md resolves in favor of the design document.
"""

from last_words.core.types import JudgeOutput, LevelConfig, LevelState

__version__ = "0.2.0"

__all__ = [
    "JudgeOutput",
    "LevelConfig",
    "LevelState",
    "__version__",
]
