"""Unit tests for the prompt loader."""

from __future__ import annotations

from pathlib import Path

import pytest

from last_words.core.prompt_loader import PromptLoadError, load_level_prompts


# Minimal valid prompts document for testing.
_VALID_PROMPTS = """
# Header

## 1. Intro

Some text.

## 2. The Bomb — Actor system prompt

```
You are a test bomb. This is the Actor prompt.
```

## 3. The Bomb — Judge system prompt

```
You are the Judge.

<transcript>
{{FULL_CONVERSATION_HISTORY}}
</transcript>
<latest>
Consultant: {{LATEST_PLAYER_MESSAGE}}
Bomb: {{LATEST_BOMB_RESPONSE}}
</latest>
```

## 4. Other

More text.
"""


def test_loads_actor_and_judge(tmp_path: Path) -> None:
    f = tmp_path / "level_test.md"
    f.write_text(_VALID_PROMPTS)
    actor, judge = load_level_prompts(f)
    assert "You are a test bomb" in actor
    assert "You are the Judge" in judge
    assert "{{FULL_CONVERSATION_HISTORY}}" in judge


def test_missing_file_raises(tmp_path: Path) -> None:
    f = tmp_path / "nope.md"
    with pytest.raises(PromptLoadError, match="not found"):
        load_level_prompts(f)


def test_missing_actor_section_raises(tmp_path: Path) -> None:
    f = tmp_path / "level_test.md"
    f.write_text("# no Actor section")
    with pytest.raises(PromptLoadError, match="Actor"):
        load_level_prompts(f)


def test_missing_judge_placeholders_raises(tmp_path: Path) -> None:
    prompts_without_placeholders = """
## 2. Actor system prompt

```
actor
```

## 3. Judge system prompt

```
judge prompt without the required placeholders
```
"""
    f = tmp_path / "level_test.md"
    f.write_text(prompts_without_placeholders)
    with pytest.raises(PromptLoadError, match="placeholders"):
        load_level_prompts(f)
