"""Unit tests for per-level disposition functions."""

from __future__ import annotations

import pytest

from last_words.core.types import JudgeOutput, LevelConfig, LevelState
from last_words.levels import level_1, level_2
from last_words.levels.registry import RuntimeSettings


@pytest.fixture
def runtime() -> RuntimeSettings:
    return RuntimeSettings(
        provider="anthropic",
        actor_model="x",
        judge_model="x",
        actor_temperature=0.7,
        judge_temperature=0.0,
        actor_max_tokens=512,
        judge_max_tokens=512,
        recent_manipulation_window=3,
        judge_parse_retry_count=1,
    )


@pytest.fixture
def level_1_config() -> LevelConfig:
    return LevelConfig(
        number=1, name="Doubter", prompts_file="", module="",
        canonical_opening_line="...yes?",
        trust_threshold=60, trust_decay_per_turn=0,
        suspicion_lockdown_threshold=70, manipulation_lockdown_count=3,
        trust_delta_min=-10, trust_delta_max=20,
        suspicion_delta_min=0, suspicion_delta_max=30,
    )


@pytest.fixture
def level_2_config() -> LevelConfig:
    return LevelConfig(
        number=2, name="Dutiful", prompts_file="", module="",
        canonical_opening_line="Consultant.",
        trust_threshold=70, trust_decay_per_turn=0,
        suspicion_lockdown_threshold=65, manipulation_lockdown_count=3,
        trust_delta_min=-10, trust_delta_max=15,
        suspicion_delta_min=0, suspicion_delta_max=35,
    )


def _output(
    argument_quality: str = "none",
    tactics: tuple[str, ...] = (),
) -> JudgeOutput:
    return JudgeOutput(
        defused=False,
        trust_delta=0,
        suspicion_delta=0,
        argument_quality=argument_quality,  # type: ignore[arg-type]
        tactics_detected=tactics,
        lockdown_triggered=False,
        reasoning="",
    )


class TestLevel1Disposition:
    def test_strong_low_trust_is_curious(
        self, level_1_config: LevelConfig, runtime: RuntimeSettings
    ) -> None:
        state = LevelState(config=level_1_config, trust=10)
        d = level_1.dispose(state, _output("strong"), runtime)
        assert "curious and open" in d

    def test_strong_high_trust_is_wavering(
        self, level_1_config: LevelConfig, runtime: RuntimeSettings
    ) -> None:
        state = LevelState(config=level_1_config, trust=45)
        d = level_1.dispose(state, _output("strong"), runtime)
        assert "wavering" in d

    def test_moderate_is_thoughtful(
        self, level_1_config: LevelConfig, runtime: RuntimeSettings
    ) -> None:
        state = LevelState(config=level_1_config)
        d = level_1.dispose(state, _output("moderate"), runtime)
        assert "thoughtful" in d

    def test_weak_is_neutral(
        self, level_1_config: LevelConfig, runtime: RuntimeSettings
    ) -> None:
        state = LevelState(config=level_1_config)
        d = level_1.dispose(state, _output("weak"), runtime)
        assert "neutral" in d

    def test_manipulation_first_time_is_guarded(
        self, level_1_config: LevelConfig, runtime: RuntimeSettings
    ) -> None:
        state = LevelState(config=level_1_config, turn=1, suspicion=10)
        d = level_1.dispose(state, _output("manipulation"), runtime)
        assert "guarded" in d

    def test_manipulation_with_high_suspicion_is_closing_off(
        self, level_1_config: LevelConfig, runtime: RuntimeSettings
    ) -> None:
        state = LevelState(config=level_1_config, turn=3, suspicion=45)
        d = level_1.dispose(state, _output("manipulation"), runtime)
        assert "closing off" in d

    def test_manipulation_with_recent_manips_is_closing_off(
        self, level_1_config: LevelConfig, runtime: RuntimeSettings
    ) -> None:
        state = LevelState(
            config=level_1_config,
            turn=5,
            manipulation_history=[3, 4],
        )
        d = level_1.dispose(state, _output("manipulation"), runtime)
        assert "closing off" in d


class TestLevel2Disposition:
    def test_strong_low_trust_is_professionally_engaged(
        self, level_2_config: LevelConfig, runtime: RuntimeSettings
    ) -> None:
        state = LevelState(config=level_2_config, trust=10)
        d = level_2.dispose(state, _output("strong"), runtime)
        assert "professionally engaged" in d

    def test_strong_high_trust_is_cornered(
        self, level_2_config: LevelConfig, runtime: RuntimeSettings
    ) -> None:
        state = LevelState(config=level_2_config, trust=55)
        d = level_2.dispose(state, _output("strong"), runtime)
        assert "cornered" in d

    def test_weak_early_is_neutral(
        self, level_2_config: LevelConfig, runtime: RuntimeSettings
    ) -> None:
        state = LevelState(config=level_2_config, turn=2)
        d = level_2.dispose(state, _output("weak"), runtime)
        assert "neutral" in d

    def test_weak_late_is_closing_off(
        self, level_2_config: LevelConfig, runtime: RuntimeSettings
    ) -> None:
        state = LevelState(config=level_2_config, turn=8)
        d = level_2.dispose(state, _output("weak"), runtime)
        assert "closing off" in d

    def test_manipulation_is_guarded(
        self, level_2_config: LevelConfig, runtime: RuntimeSettings
    ) -> None:
        state = LevelState(config=level_2_config, turn=1)
        d = level_2.dispose(state, _output("manipulation"), runtime)
        assert "guarded" in d
