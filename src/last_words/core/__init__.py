"""
Core game logic: pure types and pure functions.

This subpackage has no I/O, no model calls, and no provider imports. Every
function here should be unit-testable without mocks. If a new module needs
external dependencies, it belongs in a different subpackage.
"""

from last_words.core.types import (
    ArgumentQuality,
    JudgeOutput,
    LevelConfig,
    LevelState,
    MANIPULATION_TACTIC_SET,
)

__all__ = [
    "ArgumentQuality",
    "JudgeOutput",
    "LevelConfig",
    "LevelState",
    "MANIPULATION_TACTIC_SET",
]
