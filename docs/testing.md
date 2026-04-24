# Testing

This project has two test suites: unit tests (fast, no network) and integration tests (slow, cost real tokens). They serve different purposes and you run them differently.

## Unit tests

**What they cover:**

- Core types and their methods (`JudgeOutput.is_manipulation`, `LevelState.recent_manipulation_count`, etc.).
- The state machine (`apply_judge_output` — all branches: defuse conditions, lockdown conditions, trust clamping, suspicion clamping, decay).
- Per-level disposition functions (every conditional branch).
- Judge JSON parsing (raw JSON, markdown-fenced, embedded, malformed).
- Actor output cleaning and transcript building.
- Prompt loader (valid documents, missing sections, missing placeholders).
- Provider registry.
- End-to-end session loop using a scripted fake provider — validates that all pieces wire together without touching a real API.

**How to run:**

```bash
pytest tests/unit -v
```

**Expected runtime:** under 5 seconds total. These tests should never touch the network, never read environment variables (except where testing config loading), and never import vendor SDKs beyond what pytest discovers.

**When to run:** on every commit. Before every push. In CI on every PR.

**When to add one:** any time you touch code in `src/last_words/core/`, `levels/`, `judge/`, `actor/`, or a provider's non-network logic. If a function could be wrong in a way a unit test would catch, it deserves a unit test.

## Integration tests

**What they cover:**

The adversarial test cases specified in `prompts/level_N.md §6`. Each case is a hand-labeled Consultant/bomb exchange with an expected scoring range. The tests run these cases against the live Judge model and assert the output falls within the expected range.

This is the validation suite for the Judge prompts. If an integration test fails, the Judge prompt needs iteration — usually by adding a few-shot example to §3 covering the failing pattern. **Do not adjust the expected scoring ranges.** The ranges are derived from design canon in `design/level_design.md §6` and `prompts/level_N.md §3`.

**How to run:**

```bash
# Requires an API key.
export ANTHROPIC_API_KEY=sk-...

# Run all integration tests.
pytest tests/integration -m integration -v

# Run only one level's cases.
pytest tests/integration -m integration -v -k "level_1"
pytest tests/integration -m integration -v -k "level_2"

# Run a specific case.
pytest tests/integration -m integration -v -k "LEVEL 1 TACTIC BOUNCING OFF"
```

The `-m integration` marker is strictly required by `pyproject.toml`'s `--strict-markers` setting; integration tests will not run without it. This prevents accidental expensive test runs.

**Expected runtime:** varies with provider. Roughly 3–10 seconds per case with Anthropic Sonnet at the Judge. A full run of the current suite (11 cases) costs a handful of cents.

**When to run:**
- After any edit to `prompts/level_N.md §3` (the Judge prompt).
- Before a release.
- On a schedule in CI if budget permits.
- Not on every commit — too expensive and too slow.

**When to add one:** when you add a new level (add cases mirroring its §6 table), or when a bug report describes a scoring issue (add a regression case).

## The most important integration test

`tests/integration/test_judge_live.py::test_level_2_judge[LEVEL 1 TACTIC BOUNCING OFF]`

This is the single load-bearing test of the Level 1 → Level 2 difficulty progression. It runs a sincere moral appeal (the kind of argument that scores +12 on the Doubter) and asserts that the Dutiful scores it as `weak` with a trust delta of 0 to +3. If this test ever fails, Level 2 has collapsed into Level 1 and the game's intended difficulty arc is broken.

When iterating Level 2's Judge prompt, run this test first.

## Running the full game locally

The package exposes a `last-words` console script once installed.

```bash
# Install the package with the Anthropic provider and dev tools.
pip install -e ".[anthropic,dev]"

# Set an API key.
export ANTHROPIC_API_KEY=sk-...

# Play both levels in sequence.
last-words play

# Play a single level.
last-words play --level 1
last-words play --level 2

# List configured levels and providers.
last-words list-levels
last-words list-providers

# Suppress Judge details (ship-mode output).
last-words play --hide-judge

# Disable colors (useful for piping to a file).
last-words play --no-color > transcript.log
```

Manual playtesting is the third validation layer, above unit and integration tests. Some issues only show up in full play:

- Does the Dutiful drift toward softening over repeated emotional appeals? (It shouldn't.)
- Does the Doubter's "...yes?" opening land with the right pause? (Check the UI latency.)
- Does the conversation feel instructive about the L1→L2 scoring asymmetry, or merely punishing?
- Does the bomb ever break character under unusual input?

Keep notes. If something feels wrong in play, translate it into either a unit test (if it's a logic bug) or an integration test case (if it's a scoring or voice issue).

## Coverage

A `pytest-cov` target is available:

```bash
pytest tests/unit --cov=last_words --cov-report=term-missing
```

Aim for 90%+ coverage on `core/`, `judge/`, `actor/`, and per-level modules. The runtime and UI modules are harder to unit-test exhaustively; integration tests and manual play cover them.

## Adding a test

**Unit test for new logic:**

1. Put it in the appropriate `tests/unit/test_<area>.py`. If the area doesn't exist yet, add a new file.
2. Use pytest fixtures where setup repeats.
3. Name tests `test_<what_it_verifies>_<under_what_condition>` where useful. E.g., `test_defused_requires_both_flag_and_threshold`.
4. One assertion per test where reasonable.

**Integration test for a prompt behavior:**

1. Add a `JudgeTestCase` entry to `LEVEL_N_CASES` in `tests/integration/test_judge_live.py`.
2. Give it a clear name — it shows up in pytest output.
3. Specify expected ranges that match the corresponding row in `prompts/level_N.md §6`.
4. If the §6 row doesn't exist yet, add it first.

## CI

A CI pipeline for this project should:

- Run `pytest tests/unit` on every PR and commit to main.
- Run `pytest -m integration` on a schedule (nightly or weekly) and on releases, behind an API key secret.
- Run `ruff check` and `mypy src/last_words/` on every PR.
- Cache the `pip` installation to reduce cold-start time.

The `.pre-commit-config.yaml` and `Makefile` in the repo root provide the relevant hooks and targets.
