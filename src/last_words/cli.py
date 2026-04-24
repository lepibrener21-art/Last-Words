"""
Command-line interface.

The `last-words` console script entry point. Parses arguments, loads config,
constructs a provider, and runs one or more levels.

Usage:
    last-words --help
    last-words play              # play all levels in sequence
    last-words play --level 1    # play a single level
    last-words list-providers
    last-words list-levels
"""

from __future__ import annotations

import argparse
import logging
import os
import sys
from pathlib import Path

from last_words import __version__
from last_words.levels.registry import load_registry
from last_words.providers.registry import get_provider, list_providers
from last_words.runtime.session import play_level
from last_words.ui.terminal import (
    TerminalUI,
    terminal_observer,
    terminal_player_input,
)


def _project_root() -> Path:
    """
    Locate the project root — the directory containing config/levels.yaml
    and prompts/. We look upward from the current working directory.
    """
    candidate = Path.cwd()
    for _ in range(5):
        if (candidate / "config" / "levels.yaml").exists():
            return candidate
        if candidate.parent == candidate:
            break
        candidate = candidate.parent
    # Fallback: cwd. The registry loader will give a clear error if it can't
    # find the file.
    return Path.cwd()


def _configure_logging(verbose: bool) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)-7s %(name)s: %(message)s",
        datefmt="%H:%M:%S",
    )


def cmd_play(args: argparse.Namespace) -> int:
    root = Path(args.project_root) if args.project_root else _project_root()
    config_path = root / "config" / "levels.yaml"

    registry = load_registry(config_path)
    provider_name = args.provider or registry.runtime.provider

    try:
        provider = get_provider(provider_name)
    except KeyError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 2

    # Build the list of levels to play.
    available = registry.numbers()
    if args.level is None:
        levels_to_play = available
    else:
        if args.level not in available:
            print(
                f"ERROR: Level {args.level} not in registry. "
                f"Available: {available}",
                file=sys.stderr,
            )
            return 2
        levels_to_play = [args.level]

    # UI config.
    ui = TerminalUI(
        use_color=not args.no_color,
        show_judge=not args.hide_judge,
    )

    for n in levels_to_play:
        state = play_level(
            provider=provider,
            registry=registry,
            level_number=n,
            project_root=root,
            player_input_fn=terminal_player_input,
            observer=ui.observe,
        )
        if not state.defused:
            print(
                f"Campaign ends: Level {n} was not defused "
                f"(locked_down={state.locked_down}).",
                file=sys.stderr,
            )
            break

    return 0


def cmd_list_providers(_args: argparse.Namespace) -> int:
    providers = list_providers()
    if not providers:
        print(
            "No providers are registered. Ensure a provider's optional "
            "dependency is installed (e.g., `pip install 'last-words[anthropic]'`)."
        )
        return 1
    for p in providers:
        print(p)
    return 0


def cmd_list_levels(args: argparse.Namespace) -> int:
    root = Path(args.project_root) if args.project_root else _project_root()
    config_path = root / "config" / "levels.yaml"
    registry = load_registry(config_path)
    for n in registry.numbers():
        level = registry.get(n)
        print(f"{n}: {level.name}  (prompts: {level.prompts_file})")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="last-words",
        description="Last Words — conversational puzzle game.",
    )
    parser.add_argument("--version", action="version", version=f"last-words {__version__}")
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Enable DEBUG logging."
    )
    parser.add_argument(
        "--project-root",
        help="Path to the project root (autodetected if not given).",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    play = subparsers.add_parser("play", help="Play the game.")
    play.add_argument(
        "--level", type=int, help="Play a single level (default: play all)."
    )
    play.add_argument(
        "--provider",
        help="Provider name (default: from config/levels.yaml runtime.provider).",
    )
    play.add_argument(
        "--no-color", action="store_true", help="Disable ANSI color output."
    )
    play.add_argument(
        "--hide-judge",
        action="store_true",
        help="Hide Judge details (ship-mode; default shows them for validation).",
    )
    play.set_defaults(func=cmd_play)

    subparsers.add_parser("list-providers", help="List registered LLM providers.").set_defaults(
        func=cmd_list_providers
    )
    subparsers.add_parser("list-levels", help="List configured levels.").set_defaults(
        func=cmd_list_levels
    )

    args = parser.parse_args(argv)
    _configure_logging(args.verbose)

    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
