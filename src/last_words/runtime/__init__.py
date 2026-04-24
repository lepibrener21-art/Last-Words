"""
Runtime orchestration.

The game loop. Wires together providers, levels, Actor, Judge, state
machine, and UI into a playable session. This is the only subpackage
that coordinates all the others; keep it thin.
"""

from last_words.runtime.session import GameSession, play_level

__all__ = ["GameSession", "play_level"]
