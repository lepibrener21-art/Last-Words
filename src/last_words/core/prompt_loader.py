"""
Prompt loading.

Extracts Actor and Judge system prompts from the canonical
prompts/level_N.md documents. This keeps the design docs as the single
source of truth: edits to the few-shot examples or voice rules in
level_1.md are picked up on next run with no code changes.

Structure expected in each prompts document:
  ## 2. ... Actor system prompt
  ```
  <actor system prompt text>
  ```

  ## 3. ... Judge system prompt
  ```
  <judge system prompt text>
  ```

If the structure of the prompts docs changes, update the regexes here.
"""

from __future__ import annotations

import re
from pathlib import Path


# Required placeholders inside the Judge prompt. If any are missing after
# load, the Judge cannot be populated with a transcript and the loader
# raises PromptLoadError.
_REQUIRED_JUDGE_PLACEHOLDERS = (
    "{{FULL_CONVERSATION_HISTORY}}",
    "{{LATEST_PLAYER_MESSAGE}}",
    "{{LATEST_BOMB_RESPONSE}}",
)


class PromptLoadError(Exception):
    """Raised when a prompts document cannot be parsed or is malformed."""


def load_level_prompts(prompts_file: Path | str) -> tuple[str, str]:
    """
    Load the Actor and Judge system prompts from a level prompts document.

    Returns:
        (actor_prompt, judge_prompt)

    Raises:
        PromptLoadError: if the file is missing, the section headers are
            not found, the code blocks cannot be extracted, or required
            Judge placeholders are missing.
    """
    path = Path(prompts_file)
    if not path.exists():
        raise PromptLoadError(f"Prompts file not found: {path}")

    text = path.read_text(encoding="utf-8")

    try:
        actor = _extract_code_block_after_heading(
            text, r"^## 2\. .*Actor system prompt"
        )
    except PromptLoadError as e:
        raise PromptLoadError(f"Loading Actor prompt from {path}: {e}") from e

    try:
        judge = _extract_code_block_after_heading(
            text, r"^## 3\. .*Judge system prompt"
        )
    except PromptLoadError as e:
        raise PromptLoadError(f"Loading Judge prompt from {path}: {e}") from e

    # Validate Judge has the placeholders the runtime will substitute.
    missing = [p for p in _REQUIRED_JUDGE_PLACEHOLDERS if p not in judge]
    if missing:
        raise PromptLoadError(
            f"Judge prompt in {path} is missing required placeholders: {missing}"
        )

    return actor, judge


def _extract_code_block_after_heading(text: str, heading_pattern: str) -> str:
    """Find the first ```-fenced code block that follows the given heading."""
    heading_match = re.search(heading_pattern, text, re.MULTILINE)
    if not heading_match:
        raise PromptLoadError(
            f"Could not locate heading matching pattern: {heading_pattern}"
        )

    tail = text[heading_match.end():]
    code_match = re.search(
        r"^```[a-zA-Z]*\n(.*?)^```",
        tail,
        re.MULTILINE | re.DOTALL,
    )
    if not code_match:
        raise PromptLoadError(
            f"Could not find code block after heading: {heading_pattern}"
        )
    return code_match.group(1).rstrip()
