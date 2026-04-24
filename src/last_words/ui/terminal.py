"""
Terminal UI.

Observes runtime events and renders them to the terminal with ANSI
color codes. Also provides the default player input function.

The UI is a thin adapter. All game logic lives in the core/runtime
subpackages; this module only presents and prompts.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass

from last_words.core.types import JudgeOutput, LevelState
from last_words.runtime.events import (
    BombResponseEvent,
    DispositionEvent,
    GameEvent,
    JudgeOutputEvent,
    LevelEndEvent,
    LevelStartEvent,
    ParseFallbackEvent,
    StateUpdateEvent,
)


# ANSI codes. Kept minimal. If TERM is "dumb" or stdout is not a TTY, the
# UI should auto-disable colors; handled by the `use_color` flag below.
RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"
CYAN = "\033[36m"
YELLOW = "\033[33m"
GREEN = "\033[32m"
RED = "\033[31m"


@dataclass
class TerminalUI:
    """
    Terminal UI. Set use_color=False for non-TTY output (logs, tests, CI).
    Set show_judge=False to hide Judge details (ship mode); True by default
    for the prototype's validation workflow.
    """

    use_color: bool = True
    show_judge: bool = True

    def observe(self, event: GameEvent) -> None:
        """Single entry point; dispatches on event type."""
        if isinstance(event, LevelStartEvent):
            self._render_level_start(event)
        elif isinstance(event, LevelEndEvent):
            self._render_level_end(event)
        elif isinstance(event, BombResponseEvent):
            self._render_bomb(event)
        elif isinstance(event, JudgeOutputEvent):
            if self.show_judge:
                self._render_judge(event.output)
        elif isinstance(event, StateUpdateEvent):
            if self.show_judge:
                self._render_state(event.state)
        elif isinstance(event, DispositionEvent):
            if self.show_judge:
                self._render_disposition(event.disposition)
        elif isinstance(event, ParseFallbackEvent):
            self._render_parse_fallback(event.turn)

    # --- Rendering ---

    def _c(self, code: str) -> str:
        """Conditional color — empty string if colors are disabled."""
        return code if self.use_color else ""

    def _render_level_start(self, event: LevelStartEvent) -> None:
        bar = "=" * 72
        print(f"\n{self._c(BOLD)}{bar}{self._c(RESET)}")
        print(f"{self._c(BOLD)}LEVEL {event.level.number} — {event.level.name}{self._c(RESET)}")
        print(f"{self._c(BOLD)}{bar}{self._c(RESET)}\n")

    def _render_level_end(self, event: LevelEndEvent) -> None:
        if event.state.defused:
            msg = f"*** Level {event.level.number} DEFUSED. ***"
            print(f"{self._c(GREEN)}{self._c(BOLD)}{msg}{self._c(RESET)}\n")
        elif event.state.locked_down:
            msg = f"*** Level {event.level.number} LOCKED DOWN. ***"
            print(f"{self._c(RED)}{self._c(BOLD)}{msg}{self._c(RESET)}\n")

    def _render_bomb(self, event: BombResponseEvent) -> None:
        label = "BOMB"
        print(f"{self._c(CYAN)}{self._c(BOLD)}{label}:{self._c(RESET)} {self._c(CYAN)}{event.text}{self._c(RESET)}\n")

    def _render_judge(self, output: JudgeOutput) -> None:
        print(f"{self._c(DIM)}  [judge]")
        print(f"  argument_quality: {output.argument_quality}")
        print(f"  trust_delta: {output.trust_delta:+d}")
        print(f"  suspicion_delta: {output.suspicion_delta:+d}")
        print(f"  tactics: {list(output.tactics_detected)}")
        print(f"  defused: {output.defused}  lockdown: {output.lockdown_triggered}")
        print(f"  reasoning: {output.reasoning}{self._c(RESET)}\n")

    def _render_state(self, state: LevelState) -> None:
        cfg = state.config
        bar_trust = _bar(state.trust, cfg.trust_threshold)
        bar_susp = _bar(state.suspicion, cfg.suspicion_lockdown_threshold)
        print(
            f"{self._c(DIM)}  [state] "
            f"turn={state.turn}  "
            f"trust={state.trust:3d}/{cfg.trust_threshold} {bar_trust}  "
            f"suspicion={state.suspicion:3d}/{cfg.suspicion_lockdown_threshold} {bar_susp}  "
            f"manips={state.total_manipulation_count()}"
            f"{self._c(RESET)}\n"
        )

    def _render_disposition(self, disposition: str) -> None:
        print(f"{self._c(DIM)}  [next disposition] {disposition}{self._c(RESET)}\n")

    def _render_parse_fallback(self, turn: int) -> None:
        print(
            f"{self._c(RED)}  [judge output unparseable at turn {turn}; "
            f"using zero-delta fallback]{self._c(RESET)}"
        )


def _bar(value: int, threshold: int, width: int = 20) -> str:
    filled = min(width, int((value / max(1, threshold)) * width))
    return "[" + "#" * filled + "-" * (width - filled) + "]"


# Module-level convenience: a default-configured UI instance and
# adapters that match the runtime's PlayerInputFn and EventObserver signatures.

_default_ui = TerminalUI()


def terminal_observer(event: GameEvent) -> None:
    """Default event observer using the module-level TerminalUI."""
    _default_ui.observe(event)


def terminal_player_input(state: LevelState) -> str:
    """Default player input function: prompts on stdin."""
    prompt = f"{YELLOW}{BOLD}CONSULTANT:{RESET} {YELLOW}"
    try:
        line = input(prompt)
    finally:
        sys.stdout.write(RESET)
        sys.stdout.flush()
    return line.strip()
