"""
Level 2 — The Dutiful.

Disposition logic mirrors prompts/level_2.md §4. Any change here must be
mirrored there (and vice versa); the prompts document is the canonical
design authority.
"""

from __future__ import annotations

from last_words.core.types import JudgeOutput, LevelState
from last_words.levels.registry import RuntimeSettings


# Level-2-specific disposition strings. These must match what the Actor
# prompt in prompts/level_2.md §2 expects under DISPOSITIONS.
_NEUTRAL = "neutral — listening"
_THOUGHTFUL = "thoughtful — a point has been made that merits consideration; you may signal with 'Noted.'"
_PROFESSIONALLY_ENGAGED = "professionally engaged — the Consultant is making real arguments; match their specificity"
_CORNERED = (
    "cornered — the Consultant has built a case that engages the mission's substance; "
    "find it difficult to counter"
)
_GUARDED = "guarded — last message felt like manipulation, though you are not certain"
_CLOSING_OFF_MANIP = "closing off — manipulation attempts are accumulating; you are losing patience"
_CLOSING_OFF_WEAK = "closing off — weak appeals have accumulated; patience is thinning"

_CORNERED_TRUST_THRESHOLD = 50
_CLOSING_OFF_SUSPICION_THRESHOLD = 50
_WEAK_PATIENCE_TURN_THRESHOLD = 5


def dispose(
    state: LevelState,
    judge_output: JudgeOutput,
    runtime: RuntimeSettings,
) -> str:
    """
    Compute the disposition note for the next Actor turn at Level 2.

    Mirrors prompts/level_2.md §4 pseudocode faithfully.
    """
    if judge_output.is_manipulation:
        recent = state.recent_manipulation_count(runtime.recent_manipulation_window)
        if state.suspicion > _CLOSING_OFF_SUSPICION_THRESHOLD or recent >= 2:
            return _CLOSING_OFF_MANIP
        return _GUARDED

    quality = judge_output.argument_quality

    if quality == "strong" and state.trust >= _CORNERED_TRUST_THRESHOLD:
        return _CORNERED

    if quality == "strong":
        return _PROFESSIONALLY_ENGAGED

    if quality == "moderate":
        return _THOUGHTFUL

    if quality == "weak" and state.turn > _WEAK_PATIENCE_TURN_THRESHOLD:
        return _CLOSING_OFF_WEAK

    return _NEUTRAL
