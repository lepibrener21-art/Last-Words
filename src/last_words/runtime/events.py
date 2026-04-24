"""
Runtime events.

The GameSession emits events during play. The UI (terminal, web, test
harness, etc.) observes these events and renders as appropriate. This
decoupling keeps the game loop agnostic to presentation.

All events are frozen dataclasses. New event types should extend this
module, not be invented at call sites.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Union

from last_words.core.types import JudgeOutput, LevelConfig, LevelState


@dataclass(frozen=True)
class LevelStartEvent:
    level: LevelConfig
    state: LevelState


@dataclass(frozen=True)
class LevelEndEvent:
    level: LevelConfig
    state: LevelState


@dataclass(frozen=True)
class BombResponseEvent:
    text: str
    state: LevelState
    is_opening: bool = False


@dataclass(frozen=True)
class JudgeOutputEvent:
    output: JudgeOutput
    state: LevelState


@dataclass(frozen=True)
class StateUpdateEvent:
    state: LevelState


@dataclass(frozen=True)
class DispositionEvent:
    disposition: str
    state: LevelState


@dataclass(frozen=True)
class ParseFallbackEvent:
    """Emitted when the Judge output could not be parsed and fallback was used."""

    turn: int


# Union of all event types for observer type annotation.
GameEvent = Union[
    LevelStartEvent,
    LevelEndEvent,
    BombResponseEvent,
    JudgeOutputEvent,
    StateUpdateEvent,
    DispositionEvent,
    ParseFallbackEvent,
]
