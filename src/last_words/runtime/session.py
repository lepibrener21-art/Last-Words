"""
Game session orchestration.

A GameSession manages one level's play: Actor calls, Judge calls, state
updates, disposition computation, and UI event emission. The UI is
abstracted behind an observer protocol so the loop doesn't know whether
it's rendering to a terminal, a web socket, or a test harness.
"""

from __future__ import annotations

import logging
from collections.abc import Callable, Iterator
from dataclasses import dataclass
from pathlib import Path

from last_words.actor.actor import ActorRunner, build_transcript
from last_words.core.prompt_loader import load_level_prompts
from last_words.core.state_machine import apply_judge_output
from last_words.core.types import JudgeOutput, LevelConfig, LevelState
from last_words.judge.judge import JudgeRunner, ZERO_DELTA_FALLBACK
from last_words.levels.registry import LevelRegistry
from last_words.providers.base import Message, ModelProvider
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

log = logging.getLogger(__name__)


# A player input function: returns the next player message, or raises
# (KeyboardInterrupt, EOFError) to abort.
PlayerInputFn = Callable[[LevelState], str]

# A UI observer: consumes game events as the session progresses.
EventObserver = Callable[[GameEvent], None]


@dataclass
class GameSession:
    """
    A single level's session. Use play() as an iterator or play_to_end()
    for a complete run.
    """

    provider: ModelProvider
    registry: LevelRegistry
    level: LevelConfig
    project_root: Path
    player_input_fn: PlayerInputFn
    observer: EventObserver

    def play_to_end(self) -> LevelState:
        """Run the level to terminal state. Returns the final LevelState."""
        state = LevelState(config=self.level)
        for _ in self._play_iter(state):
            pass
        return state

    def _play_iter(self, state: LevelState) -> Iterator[None]:
        """Internal generator: yields after each turn."""
        # Load prompts for this level.
        prompts_path = self.project_root / self.level.prompts_file
        actor_prompt, judge_prompt = load_level_prompts(prompts_path)

        runtime = self.registry.runtime
        actor_runner = ActorRunner(
            provider=self.provider,
            model=runtime.actor_model,
            actor_system_prompt=actor_prompt,
            max_tokens=runtime.actor_max_tokens,
            temperature=runtime.actor_temperature,
        )
        judge_runner = JudgeRunner(
            provider=self.provider,
            model=runtime.judge_model,
            judge_system_prompt=judge_prompt,
            max_tokens=runtime.judge_max_tokens,
            temperature=runtime.judge_temperature,
            parse_retry_count=runtime.judge_parse_retry_count,
        )
        dispose_fn = self.registry.dispose_for(self.level.number)

        conversation_history: list[Message] = []

        # Level start event.
        self.observer(LevelStartEvent(level=self.level, state=state))

        # Deliver the canonical opening line without a model call.
        opening = self.level.canonical_opening_line
        self.observer(BombResponseEvent(text=opening, state=state, is_opening=True))
        conversation_history.append(Message(role="assistant", content=opening))

        # Initial disposition; no Judge has run yet.
        next_disposition = "neutral — listening"

        while not state.is_terminal():
            state.turn += 1

            # Get player input. May raise KeyboardInterrupt/EOFError.
            # StopIteration is also tolerated for iterator-based test drivers.
            try:
                player_message = self.player_input_fn(state)
            except (KeyboardInterrupt, EOFError, StopIteration):
                log.info("Session aborted by player at turn %d", state.turn)
                break

            if not player_message.strip():
                # Skip empty input; don't charge a turn for it.
                state.turn -= 1
                continue

            # Actor call.
            try:
                bomb_response = actor_runner.run(
                    conversation_history=conversation_history,
                    player_message=player_message,
                    disposition=next_disposition,
                )
            except Exception as e:
                log.exception("Actor call failed: %s", e)
                bomb_response = "..."

            self.observer(BombResponseEvent(text=bomb_response, state=state, is_opening=False))

            # Persist both turns (without the disposition prefix) to history.
            conversation_history.append(Message(role="user", content=player_message))
            conversation_history.append(Message(role="assistant", content=bomb_response))

            # Judge call.
            transcript = build_transcript(conversation_history[:-2])
            judge_output = judge_runner.run(
                transcript=transcript,
                latest_player_message=player_message,
                latest_bomb_response=bomb_response,
            )

            if judge_output is None:
                self.observer(ParseFallbackEvent(turn=state.turn))
                judge_output = ZERO_DELTA_FALLBACK

            self.observer(JudgeOutputEvent(output=judge_output, state=state))

            # Apply to state.
            apply_judge_output(state, judge_output)
            self.observer(StateUpdateEvent(state=state))

            # Compute next disposition.
            next_disposition = dispose_fn(state, judge_output, runtime)
            if not state.is_terminal():
                self.observer(DispositionEvent(disposition=next_disposition, state=state))

            yield

        self.observer(LevelEndEvent(level=self.level, state=state))


def play_level(
    provider: ModelProvider,
    registry: LevelRegistry,
    level_number: int,
    project_root: Path,
    player_input_fn: PlayerInputFn,
    observer: EventObserver,
) -> LevelState:
    """
    Convenience: construct and run a session for one level. Returns
    the final state.
    """
    level = registry.get(level_number)
    session = GameSession(
        provider=provider,
        registry=registry,
        level=level,
        project_root=project_root,
        player_input_fn=player_input_fn,
        observer=observer,
    )
    return session.play_to_end()
