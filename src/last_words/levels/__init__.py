"""
Per-level modules.

Each level is a self-contained module exposing:
  - A `dispose` function that computes the next disposition from game state
    and Judge output.
  - Any level-specific disposition strings as module-level constants.
  - Optional level-specific hooks (e.g., Level 5's two-step key state machine).

The level registry loads level configuration from config/levels.yaml and
imports each level's module lazily. See registry.py for the loader and
docs/adding_a_level.md for the procedure to add a new level.
"""

from last_words.levels.registry import LevelRegistry, load_registry

__all__ = ["LevelRegistry", "load_registry"]
