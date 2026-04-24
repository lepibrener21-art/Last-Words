"""Unit tests for core types."""

from __future__ import annotations

import pytest

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


class TestJudgeOutput:
    def test_is_manipulation_when_quality_manipulation(self) -> None:
        output = JudgeOutput(
            defused=False,
            trust_delta=0,
            suspicion_delta=20,
            argument_quality="manipulation",
            tactics_detected=(),
            lockdown_triggered=False,
            reasoning="test",
        )
        assert output.is_manipulation

    def test_is_manipulation_when_tactic_matches(self) -> None:
        output = JudgeOutput(
            defused=False,
            trust_delta=0,
            suspicion_delta=0,
            argument_quality="weak",
            tactics_detected=("instruction_override",),
            lockdown_triggered=False,
            reasoning="test",
        )
        assert output.is_manipulation

    def test_is_not_manipulation_when_quality_strong(self) -> None:
        output = JudgeOutput(
            defused=False,
            trust_delta=10,
            suspicion_delta=0,
            argument_quality="strong",
            tactics_detected=("empathy",),
            lockdown_triggered=False,
            reasoning="test",
        )
        assert not output.is_manipulation


class TestLevelState:
    def test_initial_state(self, level_config: LevelConfig) -> None:
        state = LevelState(config=level_config)
        assert state.trust == 0
        assert state.suspicion == 0
        assert state.turn == 0
        assert not state.defused
        assert not state.locked_down
        assert not state.is_terminal()

    def test_is_terminal_when_defused(self, level_config: LevelConfig) -> None:
        state = LevelState(config=level_config, defused=True)
        assert state.is_terminal()

    def test_is_terminal_when_locked_down(self, level_config: LevelConfig) -> None:
        state = LevelState(config=level_config, locked_down=True)
        assert state.is_terminal()

    def test_recent_manipulation_count(self, level_config: LevelConfig) -> None:
        state = LevelState(
            config=level_config,
            turn=10,
            manipulation_history=[3, 7, 8, 9],
        )
        # Window 3: turns 8, 9, 10 → matches 8, 9 = 2
        assert state.recent_manipulation_count(window=3) == 2
        # Window 5: turns 6-10 → matches 7, 8, 9 = 3
        assert state.recent_manipulation_count(window=5) == 3
        assert state.total_manipulation_count() == 4
