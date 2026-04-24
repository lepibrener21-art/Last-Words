"""
Actor module.

The Actor generates bomb responses. This module handles conversation
history management, disposition note injection, and output cleaning
(stripping any leaked disposition notes as defense in depth).
"""

from last_words.actor.actor import (
    ActorRunner,
    build_transcript,
    call_actor,
    clean_actor_output,
)

__all__ = [
    "ActorRunner",
    "build_transcript",
    "call_actor",
    "clean_actor_output",
]
