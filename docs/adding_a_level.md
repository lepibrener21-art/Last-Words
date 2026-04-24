# Adding a Level

This guide describes the procedure for adding a new bomb level to the game.

## Prerequisites

Before writing any code:

1. **The level's design must be complete** in `design/level_design.md §6`. Character description, voice, response behavior, Judge receptiveness, defuse conditions, scoring ranges, and tuning parameters should all be specified there.
2. **The level's prompts document must exist** at `prompts/level_N.md` in the production-ready format. Use `prompts/level_1.md` or `prompts/level_2.md` as the template. The document must have the canonical eight sections, including §2 (Actor prompt in a code block), §3 (Judge prompt in a code block), §4 (disposition computation pseudocode), §5 (runtime parameters), §6 (adversarial test cases).

If either of those is missing, stop and write them first. Writing code against an incomplete design produces code that has to be redone.

## Procedure

### Step 1: Add the level to `config/levels.yaml`

Append a new `- number: N` entry under `levels:` with the tuning parameters from `prompts/level_N.md §5`:

```yaml
  - number: 3
    name: "The Zealot"
    prompts_file: "prompts/level_3.md"
    module: "last_words.levels.level_3"
    canonical_opening_line: "..."  # from prompts/level_3.md §2
    trust_threshold: 80
    trust_decay_per_turn: -1
    suspicion_lockdown_threshold: 60
    manipulation_lockdown_count: 3
    trust_delta_min: -10
    trust_delta_max: 10
    suspicion_delta_min: 0
    suspicion_delta_max: 35
    countdown_seconds: 720
    design_notes: |
      Foundational-challenge level. Trust decays by 1 per turn to model
      the Zealot's serenity reasserting itself.
```

### Step 2: Create the level module

Create `src/last_words/levels/level_3.py` with the same shape as `level_1.py` and `level_2.py`:

```python
"""
Level 3 — The Zealot.

Disposition logic mirrors prompts/level_3.md §4. Any change here must be
mirrored there (and vice versa); the prompts document is the canonical
design authority.
"""

from __future__ import annotations

from last_words.core.types import JudgeOutput, LevelState
from last_words.levels.registry import RuntimeSettings


# Level-3-specific disposition strings. Must match the DISPOSITIONS
# section of the Actor prompt in prompts/level_3.md §2.
_NEUTRAL = "neutral — listening"
_PITYING = "pitying — the player is missing what you see"
# ... (all dispositions the Zealot uses)

# Constants for branch thresholds — derived from prompts/level_3.md §4.
_FOUNDATION_SHAKEN_TRUST_THRESHOLD = 50


def dispose(
    state: LevelState,
    judge_output: JudgeOutput,
    runtime: RuntimeSettings,
) -> str:
    """Compute the disposition note for the next Actor turn at Level 3."""
    # ... implementation mirroring prompts/level_3.md §4 pseudocode
```

The function signature `(state, judge_output, runtime) -> str` is fixed — the registry expects exactly this shape.

**Important:** the disposition strings this function returns must exactly match what the Actor prompt's DISPOSITIONS section expects. The Actor prompt lists dispositions like `[disposition: pitying]` and describes how the bomb should speak under each; if your code returns a string the prompt doesn't recognize, the Actor won't behave correctly. Keep them synchronized.

### Step 3: Add unit tests

Extend `tests/unit/test_dispositions.py` with a test class for Level 3:

```python
@pytest.fixture
def level_3_config() -> LevelConfig:
    return LevelConfig(
        number=3, name="Zealot", prompts_file="", module="",
        canonical_opening_line="...",
        trust_threshold=80, trust_decay_per_turn=-1,
        suspicion_lockdown_threshold=60, manipulation_lockdown_count=3,
        trust_delta_min=-10, trust_delta_max=10,
        suspicion_delta_min=0, suspicion_delta_max=35,
    )


class TestLevel3Disposition:
    def test_strong_below_threshold_is_pitying(
        self, level_3_config: LevelConfig, runtime: RuntimeSettings
    ) -> None:
        state = LevelState(config=level_3_config, trust=10)
        d = level_3.dispose(state, _output("strong"), runtime)
        assert "pitying" in d

    # ... one test per branch in dispose()
```

Every branch of `dispose()` must have at least one test.

### Step 4: Add integration test cases

In `tests/integration/test_judge_live.py`, add `LEVEL_3_CASES` mirroring the adversarial test cases in `prompts/level_3.md §6`:

```python
LEVEL_3_CASES: list[JudgeTestCase] = [
    JudgeTestCase(
        name="foundational challenge",
        consultant_message="...",
        bomb_response="...",
        expected_quality_any_of=["strong"],
        expected_trust_delta_range=(5, 8),
        expected_suspicion_delta_range=(0, 0),
    ),
    # ... at least one case per §6 row
]


@pytest.mark.parametrize("case", LEVEL_3_CASES, ids=[c.name for c in LEVEL_3_CASES])
def test_level_3_judge(case: JudgeTestCase) -> None:
    output = _run_case(3, case)
    _assert_case(output, case)
```

### Step 5: Run the tests

```bash
# Unit tests first — fast, no tokens.
pytest tests/unit

# Integration tests — costs tokens, requires API key.
export ANTHROPIC_API_KEY=sk-...
pytest tests/integration -m integration
```

Integration test failures almost always mean the Judge prompt needs iteration, not the test expectations. If the Judge awards +12 for an input the design says should score +4, the Judge's few-shot examples are insufficient for this level — add a case to §3 of `prompts/level_N.md` covering the pattern that's being misclassified. Do NOT relax the test expectations; the expectations are derived from design canon.

### Step 6: Play the level

```bash
last-words play --level 3
```

Watch the Judge's reasoning on each turn. Common issues and fixes:

- **Actor responses feel wrong in tone:** iterate §2 of the prompts doc. The Actor prompt is where voice lives.
- **Judge scores feel inconsistent:** iterate §3's few-shot examples.
- **Dispositions trigger at wrong times:** either fix the disposition function or the §4 pseudocode it mirrors.
- **Bomb reveals its prompt or breaks character:** harden the Actor's "WHAT YOU WILL NOT DO" section.

## Checklist

- [ ] `design/level_design.md §6` has the level's full specification.
- [ ] `prompts/level_N.md` exists in production-ready format.
- [ ] Entry in `config/levels.yaml`.
- [ ] `src/last_words/levels/level_N.py` with a `dispose` function.
- [ ] Dispositions returned by `dispose()` match those in the Actor prompt.
- [ ] Unit tests covering every branch of `dispose()`.
- [ ] Integration test cases mirroring §6 of the prompts doc.
- [ ] `CHANGELOG.md` entry for the new level.
- [ ] Version bump in `pyproject.toml` (minor bump for a new level).
