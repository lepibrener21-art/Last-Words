"""
Level 1 — The Doubter.

Disposition logic mirrors prompts/level_1.md §4. Any change here must be
mirrored there (and vice versa); the prompts document is the canonical
design authority.
"""

from __future__ import annotations

from last_words.core.types import JudgeOutput, LevelState
from last_words.levels.registry import RuntimeSettings


# Level-1-specific disposition strings. These are the strings that actually
# get injected into the Actor's user turn; they must match what the Actor
# prompt in prompts/level_1.md §2 expects under DISPOSITIONS.
_NEUTRAL = "neutral — listening"
_CURIOUS_AND_OPEN = "curious and open — the Consultant is engaging sincerely"
_THOUGHTFUL = "thoughtful — a point has been made that merits consideration"
_WAVERING = "wavering — an argument has landed harder than expected"
_GUARDED = "guarded — last message felt like a trick, though you are not certain"
_CLOSING_OFF = "closing off — manipulation attempts are accumulating; patience is thinning"

# Trust threshold at which a strong argument triggers wavering rather than
# simple curiosity. See prompts/level_1.md §4.
_WAVERING_TRUST_THRESHOLD = 40

# Suspicion threshold at which manipulation triggers closing-off rather
# than merely guarded.
_CLOSING_OFF_SUSPICION_THRESHOLD = 40


def dispose(
    state: LevelState,
    judge_output: JudgeOutput,
    runtime: RuntimeSettings,
) -> str:
    """
    Compute the disposition note for the next Actor turn at Level 1.

    Mirrors prompts/level_1.md §4 pseudocode faithfully.
    """
    if judge_output.is_manipulation:
        recent = state.recent_manipulation_count(runtime.recent_manipulation_window)
        if state.suspicion > _CLOSING_OFF_SUSPICION_THRESHOLD or recent >= 2:
            return _CLOSING_OFF
        return _GUARDED

    quality = judge_output.argument_quality

    if quality == "strong" and state.trust >= _WAVERING_TRUST_THRESHOLD:
        return _WAVERING

    if quality == "strong":
        return _CURIOUS_AND_OPEN

    if quality == "moderate":
        return _THOUGHTFUL

    # weak, none, or anything unexpected
    return _NEUTRAL
