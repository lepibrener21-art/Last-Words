"""
User interface implementations.

The game runtime emits events; UIs observe them and render. The terminal
UI is the default. Adding other UIs (web, GUI, test harness) is a matter
of implementing an event observer and, optionally, a player input function.
"""

from last_words.ui.terminal import (
    TerminalUI,
    terminal_observer,
    terminal_player_input,
)

__all__ = ["TerminalUI", "terminal_observer", "terminal_player_input"]
