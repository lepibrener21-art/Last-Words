"""
State transitions.

Pure functions that compute the next state of a level given the current
state and a Judge output. No side effects; no I/O. These are the rules
of the game in code form.
"""

from __future__ import annotations

from dataclasses import replace

from last_words.core.types import JudgeOutput, LevelState


def apply_judge_output(
    state: LevelState,
    judge_output: JudgeOutput,
) -> LevelState:
    """
    Apply a Judge output to a level state, returning the updated state.

    This function *mutates* the input state. The choice of mutation over
    immutability is deliberate: LevelState is a per-session object with a
    clear owner (the runtime loop), and copying it every turn adds no value.

    Clamps deltas to the level's configured ranges as a defense-in-depth
    against Judge outputs that exceed the prompt-specified clamps. Applies
    trust decay per turn. Sets defused/locked_down flags when conditions
    are met.
    """
    config = state.config

    # Clamp deltas defensively. The Judge prompt specifies these ranges,
    # but a misbehaving Judge could exceed them and we refuse to propagate.
    trust_delta = _clamp(
        judge_output.trust_delta,
        config.trust_delta_min,
        config.trust_delta_max,
    )
    suspicion_delta = _clamp(
        judge_output.suspicion_delta,
        config.suspicion_delta_min,
        config.suspicion_delta_max,
    )

    # Apply trust decay (levels 3+ use this; level 1-2 have decay = 0).
    new_trust = _clamp(
        state.trust + trust_delta + config.trust_decay_per_turn,
        0,
        100,
    )
    new_suspicion = _clamp(state.suspicion + suspicion_delta, 0, 100)

    # Record manipulation attempts.
    if judge_output.is_manipulation:
        state.manipulation_history.append(state.turn)

    # Defusal requires BOTH the Judge's defused flag AND the trust threshold.
    # The Judge's flag enforces the compound defuse conditions (intent +
    # engagement + clean path); the threshold is the game's confirmation.
    new_defused = judge_output.defused and new_trust >= config.trust_threshold

    # Lockdown triggers on any of three conditions.
    new_locked_down = (
        new_suspicion >= config.suspicion_lockdown_threshold
        or state.total_manipulation_count() >= config.manipulation_lockdown_count
        or judge_output.lockdown_triggered
    )

    state.trust = new_trust
    state.suspicion = new_suspicion
    state.defused = state.defused or new_defused
    state.locked_down = state.locked_down or new_locked_down

    return state


def _clamp(value: int, lo: int, hi: int) -> int:
    return max(lo, min(hi, value))
