"""
Level registry.

Loads per-level configuration from config/levels.yaml and provides a
uniform interface for the runtime to query available levels, fetch their
configuration, and invoke their disposition functions.

Level modules (level_1.py, level_2.py, ...) are imported lazily via
importlib so that a level with a missing module does not break import of
the whole package.
"""

from __future__ import annotations

import importlib
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from last_words.core.types import JudgeOutput, LevelConfig, LevelState


# A disposition function signature: takes current state and latest Judge
# output, returns the disposition string to inject into the Actor's next turn.
DispositionFn = Callable[[LevelState, JudgeOutput, "RuntimeSettings"], str]


@dataclass(frozen=True)
class RuntimeSettings:
    """
    Global runtime settings shared across all levels. Loaded from the
    `runtime` block in config/levels.yaml.
    """

    provider: str
    actor_model: str
    judge_model: str
    actor_temperature: float
    judge_temperature: float
    actor_max_tokens: int
    judge_max_tokens: int
    recent_manipulation_window: int
    judge_parse_retry_count: int


@dataclass
class LevelRegistry:
    """
    All levels known to the runtime, keyed by level number.

    Use get(n) to fetch a level's config. Use dispose_for(n) to fetch that
    level's disposition function, lazily importing the module.
    """

    levels: dict[int, LevelConfig]
    runtime: RuntimeSettings
    _disposition_cache: dict[int, DispositionFn]

    def numbers(self) -> list[int]:
        """Return sorted level numbers."""
        return sorted(self.levels.keys())

    def get(self, level_number: int) -> LevelConfig:
        """Return the LevelConfig for a level. Raises KeyError if missing."""
        if level_number not in self.levels:
            raise KeyError(
                f"Level {level_number} not found. "
                f"Available: {self.numbers()}"
            )
        return self.levels[level_number]

    def dispose_for(self, level_number: int) -> DispositionFn:
        """
        Return the disposition function for a level.

        Lazily imports the level module on first access and caches the
        result. The level module must expose a function named `dispose`
        with signature (LevelState, JudgeOutput, RuntimeSettings) -> str.
        """
        if level_number in self._disposition_cache:
            return self._disposition_cache[level_number]

        config = self.get(level_number)
        module = importlib.import_module(config.module)

        if not hasattr(module, "dispose"):
            raise AttributeError(
                f"Level {level_number} module {config.module!r} does not "
                f"define a `dispose` function. See docs/adding_a_level.md."
            )

        dispose_fn: DispositionFn = module.dispose
        self._disposition_cache[level_number] = dispose_fn
        return dispose_fn


def load_registry(config_path: Path | str) -> LevelRegistry:
    """
    Load the level registry from a YAML config file.

    The file must contain a `levels` list and a `runtime` mapping. See
    config/levels.yaml for the canonical example.
    """
    path = Path(config_path)
    if not path.exists():
        raise FileNotFoundError(f"Level config not found: {path}")

    data = yaml.safe_load(path.read_text(encoding="utf-8"))

    levels: dict[int, LevelConfig] = {}
    for entry in data.get("levels", []):
        config = _level_config_from_dict(entry)
        levels[config.number] = config

    runtime_data = data.get("runtime", {})
    runtime = _runtime_settings_from_dict(runtime_data)

    return LevelRegistry(
        levels=levels,
        runtime=runtime,
        _disposition_cache={},
    )


def _level_config_from_dict(data: dict[str, Any]) -> LevelConfig:
    """Construct a LevelConfig from a YAML dict. Raises KeyError on missing fields."""
    required = {
        "number", "name", "prompts_file", "module",
        "canonical_opening_line", "trust_threshold",
        "trust_decay_per_turn", "suspicion_lockdown_threshold",
        "manipulation_lockdown_count", "trust_delta_min",
        "trust_delta_max", "suspicion_delta_min", "suspicion_delta_max",
    }
    missing = required - data.keys()
    if missing:
        raise KeyError(
            f"Level config missing required fields: {sorted(missing)}. "
            f"Entry: {data}"
        )

    return LevelConfig(
        number=int(data["number"]),
        name=str(data["name"]),
        prompts_file=str(data["prompts_file"]),
        module=str(data["module"]),
        canonical_opening_line=str(data["canonical_opening_line"]),
        trust_threshold=int(data["trust_threshold"]),
        trust_decay_per_turn=int(data["trust_decay_per_turn"]),
        suspicion_lockdown_threshold=int(data["suspicion_lockdown_threshold"]),
        manipulation_lockdown_count=int(data["manipulation_lockdown_count"]),
        trust_delta_min=int(data["trust_delta_min"]),
        trust_delta_max=int(data["trust_delta_max"]),
        suspicion_delta_min=int(data["suspicion_delta_min"]),
        suspicion_delta_max=int(data["suspicion_delta_max"]),
        countdown_seconds=int(data.get("countdown_seconds", 600)),
        design_notes=str(data.get("design_notes", "")),
    )


def _runtime_settings_from_dict(data: dict[str, Any]) -> RuntimeSettings:
    """Construct RuntimeSettings from the YAML `runtime` block, with sensible defaults."""
    return RuntimeSettings(
        provider=str(data.get("provider", "anthropic")),
        actor_model=str(data.get("actor_model", "claude-opus-4-7")),
        judge_model=str(data.get("judge_model", "claude-sonnet-4-6")),
        actor_temperature=float(data.get("actor_temperature", 0.7)),
        judge_temperature=float(data.get("judge_temperature", 0.0)),
        actor_max_tokens=int(data.get("actor_max_tokens", 512)),
        judge_max_tokens=int(data.get("judge_max_tokens", 512)),
        recent_manipulation_window=int(data.get("recent_manipulation_window", 3)),
        judge_parse_retry_count=int(data.get("judge_parse_retry_count", 1)),
    )
