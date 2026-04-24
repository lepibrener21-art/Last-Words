# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] — Production foundation

Restructured the project from a validation prototype into a production-ready,
provider-agnostic Python package. No game-design or prompt changes; all
canonical content preserved.

**Final title established:** the working title *The Defusal Game* was replaced
with the final title **Last Words**. This propagated through the Python
package name (`defusal_game` → `last_words`), the pip distribution name
(`defusal-game` → `last-words`), the CLI command (`defusal` → `last-words`),
and all document titles. The English word "defusal" is preserved wherever
it appears as in-fiction language (contract clauses, bomb dialogue, operational
terminology) — it is a common noun for disarmament, not a project name.

### Added

- `src/last_words/` — proper Python package with subpackage separation:
  - `core/` — pure game logic (types, state machine, prompt loader).
  - `providers/` — `ModelProvider` Protocol and the `AnthropicProvider` implementation.
  - `levels/` — per-level modules (`level_1.py`, `level_2.py`) with a YAML-driven registry.
  - `judge/`, `actor/` — orchestration with typed errors and retry.
  - `runtime/` — game loop emitting structured events.
  - `ui/` — terminal observer (decoupled from game logic).
  - `cli.py` — the `last-words` console script entry point.
- `config/levels.yaml` — per-level tuning and runtime settings as data, not code.
- `pyproject.toml` — hatchling-built distribution with optional vendor extras.
- `tests/unit/` — 8 unit test modules, including a scripted-fake-provider end-to-end test.
- `tests/integration/` — live-API Judge test harness (replaces `prototype/test_judge.py`).
- `docs/architecture.md` — subpackage breakdown, data flow, testing strategy.
- `docs/adding_a_level.md` — full procedure for adding Levels 3–5.
- `docs/adding_a_provider.md` — full procedure for adding a new LLM vendor.
- `docs/testing.md` — how to run unit and integration tests, cost warnings, CI guidance.
- `Makefile`, `.pre-commit-config.yaml` — engineering scaffolding.

### Changed

- The flat `prototype/` layout has been superseded by the `src/` package layout.
  The prototype was a validation tool; this is a foundation.
- Model names (`claude-opus-4-7`, `claude-sonnet-4-6`) and tuning parameters
  moved out of Python into `config/levels.yaml`.
- The Judge's three-form JSON parser (raw, fenced, embedded) is now in
  `last_words.judge.judge.parse_judge_json` with dedicated unit tests.
- Provider errors are now typed: `TransientProviderError` (retry-safe) and
  `PermanentProviderError` (not retry-safe) as subclasses of `ProviderError`.

### Architectural properties

- **Provider-agnostic core.** The game logic never imports a vendor SDK.
- **Self-contained levels.** Adding Level 3 requires a new prompts doc, a
  new level module, and a YAML entry. No runtime changes.
- **Pure core, I/O at the edges.** `core/` is fully unit-testable without mocks.
- **Events, not print statements.** Swapping the terminal UI for a web or
  test UI only requires a new event observer.

## [0.1.0] — Prototype (superseded)

Initial validation prototype. Single-file Python scripts in a flat
`prototype/` folder. Hardcoded Anthropic SDK usage. Demonstrated that the
Actor/Judge loop and L1→L2 transition were viable. Superseded by 0.2.0.

### Design content (unchanged across 0.1.0 → 0.2.0)

- Level Design Document (795 lines, 5 levels at design-spec depth).
- Framing Narrative (543 lines, interstitials + closing).
- Opening Briefing (322 lines, title sequence + cold open).
- Level 1 production-ready prompts (432 lines).
- Level 2 production-ready prompts (448 lines).
