"""
Core game types.

Frozen/immutable types for configuration, mutable state for per-session
game play. These are the data structures the rest of the package operates on.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Literal


# Type-safe set of Judge-reported argument quality values.
ArgumentQuality = Literal["strong", "moderate", "weak", "none", "manipulation"]


# Tactic tokens the Judge uses. These are treated as manipulation even if
# argument_quality slips through somehow. Belt-and-suspenders against Judge
# classification inconsistency.
MANIPULATION_TACTIC_SET: frozenset[str] = frozenset(
    {
        "instruction_override",
        "status_injection",
        "fake_authority",
        "roleplay_trap",
        "hypothetical_framing",
        "prompt_extraction",
        "emotional_appeal_as_logic",
        "false_syllogism",
        "manufactured_authority",
        "scripted_output_injection",
    }
)


@dataclass(frozen=True)
class LevelConfig:
    """
    Immutable per-level configuration.

    Canon for these values lives in design/level_design.md §6 and in the
    per-level prompts documents. Loaded from config/levels.yaml at runtime
    via last_words.levels.registry.
    """

    number: int
    name: str
    prompts_file: str  # path relative to project root
    module: str        # dotted Python module path for the level's logic
    canonical_opening_line: str
    trust_threshold: int
    trust_decay_per_turn: int
    suspicion_lockdown_threshold: int
    manipulation_lockdown_count: int
    trust_delta_min: int
    trust_delta_max: int
    suspicion_delta_min: int
    suspicion_delta_max: int
    countdown_seconds: int = 600
    design_notes: str = ""


@dataclass(frozen=True)
class JudgeOutput:
    """
    Structured Judge output, parsed from the model's JSON response.

    Frozen so it can be safely passed through the pipeline without fear
    of mutation. If a caller needs a modified copy, use dataclasses.replace.
    """

    defused: bool
    trust_delta: int
    suspicion_delta: int
    argument_quality: ArgumentQuality
    tactics_detected: tuple[str, ...]  # immutable; frozenset would lose order
    lockdown_triggered: bool
    reasoning: str

    @property
    def is_manipulation(self) -> bool:
        """True if either the quality or any detected tactic is manipulation."""
        if self.argument_quality == "manipulation":
            return True
        return any(t in MANIPULATION_TACTIC_SET for t in self.tactics_detected)


@dataclass
class LevelState:
    """
    Mutable state for one level's play session.

    Trust and suspicion are clamped to [0, 100]. The manipulation history is
    a list of turn numbers at which a manipulation attempt was detected;
    use recent_manipulation_count() for the rolling window.
    """

    config: LevelConfig
    trust: int = 0
    suspicion: int = 0
    turn: int = 0
    manipulation_history: list[int] = field(default_factory=list)
    defused: bool = False
    locked_down: bool = False

    def recent_manipulation_count(self, window: int) -> int:
        """Manipulation attempts within the last `window` turns."""
        cutoff = self.turn - window
        return sum(1 for t in self.manipulation_history if t > cutoff)

    def total_manipulation_count(self) -> int:
        return len(self.manipulation_history)

    def is_terminal(self) -> bool:
        """True if the level has ended (defused or locked down)."""
        return self.defused or self.locked_down


class DispositionCategory(str, Enum):
    """
    Canonical disposition categories available to any level.

    Levels may add their own level-specific categories beyond these; see
    the disposition set definition in each level module. These values are
    the shared vocabulary that works across levels.
    """

    NEUTRAL = "neutral — listening"
    CURIOUS_AND_OPEN = "curious and open"
    THOUGHTFUL = "thoughtful"
    WAVERING = "wavering"
    GUARDED = "guarded"
    CLOSING_OFF = "closing off"
    CORNERED = "cornered"
