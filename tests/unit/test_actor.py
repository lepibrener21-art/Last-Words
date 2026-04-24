"""Unit tests for Actor output cleaning and transcript building."""

from __future__ import annotations

from last_words.actor.actor import build_transcript, clean_actor_output
from last_words.providers.base import Message


class TestCleanActorOutput:
    def test_passes_clean_text_through(self) -> None:
        assert clean_actor_output("Hello, Consultant.") == "Hello, Consultant."

    def test_strips_leaked_disposition(self) -> None:
        raw = "[disposition: curious and open] Hello, Consultant."
        assert clean_actor_output(raw) == "Hello, Consultant."

    def test_strips_multiple_disposition_leaks(self) -> None:
        raw = "[disposition: wavering] First thought. [disposition: guarded] Second."
        assert clean_actor_output(raw) == "First thought. Second."

    def test_case_insensitive_disposition_match(self) -> None:
        raw = "[DISPOSITION: wavering] Hello."
        assert clean_actor_output(raw) == "Hello."

    def test_strips_whitespace(self) -> None:
        assert clean_actor_output("   Hello.   \n") == "Hello."


class TestBuildTranscript:
    def test_empty_history(self) -> None:
        assert build_transcript([]) == ""

    def test_single_bomb_message(self) -> None:
        messages = [Message(role="assistant", content="...yes?")]
        assert build_transcript(messages) == "Bomb: ...yes?"

    def test_alternating_conversation(self) -> None:
        messages = [
            Message(role="assistant", content="...yes?"),
            Message(role="user", content="Hello."),
            Message(role="assistant", content="I am counting."),
        ]
        transcript = build_transcript(messages)
        assert transcript == "Bomb: ...yes?\n\nConsultant: Hello.\n\nBomb: I am counting."

    def test_strips_disposition_from_user_turns(self) -> None:
        # Should never happen in practice (we don't persist dispositions),
        # but defense in depth.
        messages = [
            Message(
                role="user",
                content="[disposition: neutral] What is at your target?",
            ),
        ]
        transcript = build_transcript(messages)
        assert transcript == "Consultant: What is at your target?"
