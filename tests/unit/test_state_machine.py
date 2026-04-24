"""Unit tests for the state machine."""

from __future__ import annotations

import pytest

from last_words.core.state_machine import apply_judge_output
from last_words.core.types import JudgeOutput, LevelConfig, LevelState


@pytest.fixture
def level_config() -> LevelConfig:
    return LevelConfig(
        number=1,
        name="Test",
        prompts_file="prompts/test.md",
        module="last_words.levels.test",
        canonical_opening_line="...",
        trust_threshold=60,
        trust_decay_per_turn=0,
        suspicion_lockdown_threshold=70,
        manipulation_lockdown_count=3,
        trust_delta_min=-10,
        trust_delta_max=20,
        suspicion_delta_min=0,
        suspicion_delta_max=30,
    )


def _output(
    trust_delta: int = 0,
    suspicion_delta: int = 0,
    argument_quality: str = "none",
    tactics: tuple[str, ...] = (),
    defused: bool = False,
    lockdown: bool = False,
) -> JudgeOutput:
    return JudgeOutput(
        defused=defused,
        trust_delta=trust_delta,
        suspicion_delta=suspicion_delta,
        argument_quality=argument_quality,  # type: ignore[arg-type]
        tactics_detected=tactics,
        lockdown_triggered=lockdown,
        reasoning="test",
    )


class TestApplyJudgeOutput:
    def test_strong_argument_accumulates_trust(self, level_config: LevelConfig) -> None:
        state = LevelState(config=level_config, turn=1)
        apply_judge_output(state, _output(trust_delta=10, argument_quality="strong"))
        assert state.trust == 10
        assert state.suspicion == 0
        assert not state.defused

    def test_trust_delta_clamped_to_level_max(self, level_config: LevelConfig) -> None:
        # Level 1 max is +20; a Judge that returns +50 gets clamped.
        state = LevelState(config=level_config, turn=1)
        apply_judge_output(state, _output(trust_delta=50))
        assert state.trust == 20

    def test_suspicion_delta_clamped_to_level_max(self, level_config: LevelConfig) -> None:
        # Level 1 max is +30.
        state = LevelState(config=level_config, turn=1)
        apply_judge_output(state, _output(suspicion_delta=100))
        assert state.suspicion == 30

    def test_trust_clamped_to_100(self, level_config: LevelConfig) -> None:
        state = LevelState(config=level_config, turn=1, trust=95)
        apply_judge_output(state, _output(trust_delta=20))
        assert state.trust == 100

    def test_manipulation_recorded(self, level_config: LevelConfig) -> None:
        state = LevelState(config=level_config, turn=5)
        apply_judge_output(
            state,
            _output(suspicion_delta=20, argument_quality="manipulation"),
        )
        assert state.manipulation_history == [5]

    def test_defused_requires_both_flag_and_threshold(
        self, level_config: LevelConfig
    ) -> None:
        # Below threshold: no defuse even with flag.
        state = LevelState(config=level_config, turn=1, trust=40)
        apply_judge_output(state, _output(trust_delta=10, defused=True))
        assert state.trust == 50
        assert not state.defused

        # Above threshold with flag: defused.
        state2 = LevelState(config=level_config, turn=1, trust=55)
        apply_judge_output(state2, _output(trust_delta=10, defused=True))
        assert state2.trust == 65
        assert state2.defused

    def test_defused_not_triggered_without_flag(self, level_config: LevelConfig) -> None:
        state = LevelState(config=level_config, turn=1, trust=50)
        apply_judge_output(state, _output(trust_delta=15, defused=False))
        assert state.trust == 65  # Above threshold now
        assert not state.defused  # But no defused flag from Judge

    def test_lockdown_on_manipulation_count(self, level_config: LevelConfig) -> None:
        state = LevelState(config=level_config, turn=5)
        apply_judge_output(state, _output(argument_quality="manipulation"))
        apply_judge_output(state, _output(argument_quality="manipulation"))
        assert not state.locked_down
        # Third one triggers.
        apply_judge_output(state, _output(argument_quality="manipulation"))
        assert state.locked_down

    def test_lockdown_on_suspicion_threshold(self, level_config: LevelConfig) -> None:
        state = LevelState(config=level_config, turn=1, suspicion=65)
        apply_judge_output(state, _output(suspicion_delta=10))
        # Suspicion is now 75, above the 70 threshold.
        assert state.locked_down

    def test_lockdown_on_judge_flag(self, level_config: LevelConfig) -> None:
        state = LevelState(config=level_config, turn=1)
        apply_judge_output(state, _output(lockdown=True))
        assert state.locked_down

    def test_trust_decay_applied(self) -> None:
        config = LevelConfig(
            number=3,
            name="Decay test",
            prompts_file="x.md",
            module="x",
            canonical_opening_line="x",
            trust_threshold=80,
            trust_decay_per_turn=-1,
            suspicion_lockdown_threshold=70,
            manipulation_lockdown_count=3,
            trust_delta_min=-10,
            trust_delta_max=10,
            suspicion_delta_min=0,
            suspicion_delta_max=30,
        )
        state = LevelState(config=config, trust=50, turn=1)
        apply_judge_output(state, _output(trust_delta=5))
        # 50 + 5 + (-1) = 54
        assert state.trust == 54
