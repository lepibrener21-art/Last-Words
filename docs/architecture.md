# Architecture

This document describes how the codebase is organized and why. It is intended for engineers contributing to the project. For the game design itself, see `../design/level_design.md`.

## Guiding principles

**Design documents are the source of truth.** The files in `design/` and `prompts/` are the canonical specification. Code implements that specification. When code and a design document disagree, the design document wins. The code is structured so that design-document edits propagate automatically where possible (e.g., the prompt loader reads `prompts/level_N.md` directly at runtime).

**Provider-agnostic core.** The game logic does not know which LLM it is talking to. All vendor-specific code is quarantined to `providers/*_provider.py`. Adding a new provider does not require changes to any other subpackage.

**Self-contained levels.** Each level is a Python module under `levels/` implementing a single function: `dispose(state, judge_output, runtime) -> str`. Adding a level does not require changes to the runtime. Levels are discovered via `config/levels.yaml`.

**Pure core, I/O at the edges.** The `core/` subpackage is pure: no I/O, no model calls. This makes it fully unit-testable without mocks. Provider calls happen in `providers/`, file I/O in `core/prompt_loader.py` (file reads only) and `levels/registry.py` (config loading).

**Events, not print statements.** The runtime emits events; UIs observe them. The game loop doesn't know whether it's rendering to a terminal, a web socket, or a test harness.

## Subpackages

```
src/last_words/
├── core/           # Pure types and pure functions. No I/O, no models.
├── providers/      # LLM abstraction. ModelProvider protocol + implementations.
├── levels/         # Per-level modules + YAML-driven registry.
├── judge/          # Judge orchestration: prompt substitution, parsing, retry.
├── actor/          # Actor orchestration: conversation management, output cleaning.
├── runtime/        # Game loop and event types.
├── ui/             # Presentation (terminal default).
└── cli.py          # Command-line entry point.
```

### `core/`

- `types.py` — Frozen dataclasses for `JudgeOutput`, `LevelConfig`. Mutable `LevelState` for per-session game state. The `MANIPULATION_TACTIC_SET` constant. All types the rest of the codebase operates on live here.
- `state_machine.py` — `apply_judge_output(state, judge_output)`: the pure state transition function. Clamps deltas, applies decay, checks defuse and lockdown conditions. No I/O.
- `prompt_loader.py` — `load_level_prompts(path)`: extracts Actor and Judge prompts from a `prompts/level_N.md` document. Validates that required placeholders are present. Raises `PromptLoadError` on failure.

### `providers/`

- `base.py` — The `ModelProvider` Protocol and the neutral request/response types (`CompletionRequest`, `CompletionResponse`, `Message`). Typed exceptions (`ProviderError`, `TransientProviderError`, `PermanentProviderError`).
- `registry.py` — `register_provider(name, factory)`, `get_provider(name)`, `list_providers()`. Providers self-register at import time; failure to import a provider module (e.g., missing SDK) is silent.
- `anthropic_provider.py` — The Anthropic implementation. Maps Anthropic-specific exceptions to the typed provider exceptions.

### `levels/`

- `registry.py` — `LevelRegistry`, `load_registry(path)`, `RuntimeSettings`. Loads `config/levels.yaml` and provides lazy access to per-level disposition functions.
- `level_1.py`, `level_2.py`, ... — Each level's `dispose(state, judge_output, runtime) -> str` function. Mirrors the pseudocode in the corresponding `prompts/level_N.md` §4.

### `judge/`

- `judge.py` — `JudgeRunner` (stateful convenience), `call_judge` (function interface), `parse_judge_json` (three-form parser with fallback). Substitutes placeholders, calls the provider, parses JSON, retries on failure. Never crashes the session on parse failure — returns `None` and the runtime falls back to zero-delta.

### `actor/`

- `actor.py` — `ActorRunner`, `call_actor`, `build_transcript`, `clean_actor_output`. Handles conversation history as user/assistant turns, injects the disposition note into the current turn only, strips any leaked `[disposition: ...]` blocks from output.

### `runtime/`

- `session.py` — `GameSession` and `play_level`. The game loop. Orchestrates Actor calls, Judge calls, state updates, disposition computation, and event emission.
- `events.py` — Frozen dataclasses for each event type emitted by the game loop. UIs observe these.

### `ui/`

- `terminal.py` — `TerminalUI` (event observer with ANSI rendering), `terminal_player_input` (default stdin prompt). The only UI in the tree; others can be added as new modules and wired through the CLI.

### `cli.py`

The `last-words` console script. Parses arguments, loads config, constructs a provider, and invokes `runtime.session.play_level` for each level requested.

## Data flow for one turn

```
1. Player sends message
   └── CLI (or other UI) passes to player_input_fn

2. GameSession collects the player message
   │
   ├── Builds conversation history (list of Message objects)
   │
   └── ActorRunner.run(history, player_message, disposition)
       │
       ├── Prepends [disposition: ...] to the current turn's user message
       ├── Calls provider.complete(request)
       └── Returns cleaned Actor output

3. Bomb response shown to player (via BombResponseEvent)

4. Conversation history extended with both turns (no disposition prefix persisted)

5. JudgeRunner.run(transcript, player_message, bomb_response)
   │
   ├── Substitutes {{FULL_CONVERSATION_HISTORY}}, {{LATEST_PLAYER_MESSAGE}},
   │   {{LATEST_BOMB_RESPONSE}} into the Judge prompt template
   ├── Calls provider.complete(request) at temperature 0
   ├── parse_judge_json() tries raw / fenced / embedded JSON extraction
   ├── Retries once on parse failure
   └── Returns JudgeOutput or None

6. apply_judge_output(state, judge_output)
   │
   ├── Clamps deltas to level config bounds
   ├── Applies trust/suspicion changes and decay
   ├── Records manipulation attempts
   └── Sets defused/locked_down flags

7. State and Judge output emitted as events

8. Disposition function for this level computes the next disposition
   dispose(state, judge_output, runtime) -> str

9. Loop repeats until state.is_terminal()
```

## Error handling

**Transient provider failures** (5xx, 429, network) raise `TransientProviderError`. Callers may retry; the `JudgeRunner` retries once by default. The Actor does not retry — if the Actor fails, the runtime logs and inserts a fallback `...` response so the session continues.

**Permanent provider failures** (auth, 4xx except 429) raise `PermanentProviderError`. These propagate out of the session and terminate the run with a user-visible message.

**Judge parse failures** are the one case we silently tolerate: if the Judge returns unparseable output after retries, the runtime emits a `ParseFallbackEvent` and applies a zero-delta `JudgeOutput` so the session continues. Playtesters can see parse failures in the event log.

**User abort** (Ctrl-C, EOF) is caught in the session loop; the run ends with the current state.

## Testing strategy

**Unit tests** (`tests/unit/`) run without any external dependencies. They cover:
- Core types (`JudgeOutput`, `LevelState` methods).
- State machine (`apply_judge_output` under all conditions).
- Disposition functions (every branch for every level).
- Judge JSON parser (raw, fenced, embedded, malformed).
- Actor output cleaning and transcript building.
- Prompt loader (valid docs, missing sections, missing placeholders).
- Provider registry.
- End-to-end with a `ScriptedFakeProvider` — full session loop without real API calls.

**Integration tests** (`tests/integration/`) require `ANTHROPIC_API_KEY` and cost tokens. They validate the actual Judge prompts against the adversarial cases specified in `prompts/level_N.md §6`. Run explicitly with `pytest -m integration`.

CI should run unit tests on every commit and integration tests on a schedule or PR merge, depending on cost tolerance.

## Where to make changes

| Change | Edit |
|---|---|
| Adjust scoring range for Level 2 | `prompts/level_2.md` §3 (Judge prompt) AND §5 (runtime params) AND `config/levels.yaml`. The clamps in `core/state_machine.py` are already driven by config. |
| Add a new LLM provider | New module in `providers/`, register in `providers/registry.py`, add optional extra in `pyproject.toml`. See `docs/adding_a_provider.md`. |
| Add Level 3 | New `prompts/level_3.md`, new `src/last_words/levels/level_3.py`, new entry in `config/levels.yaml`, tests in `tests/unit/test_dispositions.py`, integration cases in `tests/integration/test_judge_live.py`. See `docs/adding_a_level.md`. |
| Change the canonical opening line of a bomb | `prompts/level_N.md` §2 (Actor prompt, opening-line section) AND `config/levels.yaml` (`canonical_opening_line` for that level). |
| Change the disposition system | `core/types.py` (`DispositionCategory` if adding a canonical category), the affected level modules, and the corresponding `prompts/level_N.md` §4. |
| Add a UI (web, GUI, etc.) | New module in `ui/`. Implement an event observer and, optionally, a player input function. Wire it into `cli.py`. |

## Versioning

Version is tracked in `pyproject.toml` and exposed as `last_words.__version__`. Prompt changes that affect scoring behavior warrant a minor bump. Internal refactors that preserve behavior warrant a patch bump. Breaking API or canon changes warrant a major bump. `CHANGELOG.md` tracks the rationale for every version.
