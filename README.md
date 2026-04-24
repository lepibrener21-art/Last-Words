# Last Words

**A conversational puzzle game where the player talks a sentient AI bomb out of detonating.**

The player is cast as the *Senior Explosive Consultant* and must negotiate with five successively harder-to-reach AI-armed bombs. The game is a homage, in its tonal register, to Douglas Adams' *Hitchhiker's Guide to the Galaxy*, concentrated in specific channels rather than evenly applied.

This repository contains the full design documentation and a production-ready, provider-agnostic Python runtime.

## Start here

**If you are designing or writing for the game:** read the documents in `design/`, starting with `design/opening_briefing.md` (for tone), then `design/level_design.md` (canonical source of truth for the game's world, characters, and mechanics), then `design/framing_narrative.md` (for interstitials and closing).

**If you are implementing or extending the code:** read `docs/architecture.md` for the subpackage breakdown, then `docs/adding_a_level.md` or `docs/adding_a_provider.md` depending on what you want to do.

**If you want to run the game:** install and play.

```bash
pip install -e ".[anthropic,dev]"
export ANTHROPIC_API_KEY=sk-...
last-words play
```

## Layout

```
/
├── README.md                   ← you are here
├── CHANGELOG.md
├── pyproject.toml              ← package build, lint, and type-check config
├── Makefile                    ← common tasks (install, test, lint, play)
├── .pre-commit-config.yaml
│
├── design/                     ← canonical design documents
│   ├── level_design.md         ← CANONICAL source of truth for fiction and mechanics
│   ├── framing_narrative.md    ← interstitials and closing
│   └── opening_briefing.md     ← title sequence and cold open
│
├── prompts/                    ← production-ready Actor and Judge prompts per level
│   ├── level_1.md              ← The Doubter
│   └── level_2.md              ← The Dutiful
│   # level_3.md, level_4.md, level_5.md pending — see docs/adding_a_level.md
│
├── config/
│   └── levels.yaml             ← per-level tuning and runtime settings
│
├── src/last_words/           ← the Python package
│   ├── core/                   ← pure types and pure functions
│   ├── providers/              ← LLM abstraction + Anthropic implementation
│   ├── levels/                 ← per-level modules and registry
│   ├── judge/                  ← Judge orchestration, JSON parsing, retry
│   ├── actor/                  ← Actor orchestration, output cleaning
│   ├── runtime/                ← game loop and event types
│   ├── ui/                     ← presentation (terminal default)
│   └── cli.py                  ← `last-words` console script
│
├── tests/
│   ├── unit/                   ← fast, no network, no API keys
│   └── integration/            ← live Judge validation (requires API key)
│
└── docs/                       ← engineering documentation
    ├── architecture.md         ← subpackage breakdown + data flow
    ├── adding_a_level.md       ← procedure for Levels 3–5
    ├── adding_a_provider.md    ← procedure for OpenAI, Google, local, etc.
    └── testing.md              ← how to run tests and when
```

## The canonical authority

**`design/level_design.md` is the single source of truth** for the game's fiction, characters, and mechanics. Any conflict between documents — or between a document and the code — resolves in favor of the level design doc. The other documents specify how the canon appears in specific parts of the game:

- `design/opening_briefing.md` — how canon appears in the opening.
- `design/framing_narrative.md` — how canon appears between levels.
- `prompts/level_N.md` — how canon becomes runnable prompts.
- `config/levels.yaml` + `src/last_words/` — how prompts become a running game.

If you edit canon, edit `design/level_design.md` first, then update the downstream documents, then update the code where relevant.

## Architectural properties

Three properties were load-bearing in the production structure:

1. **Provider-agnostic core.** The game logic never imports a vendor SDK. All LLM calls go through the `ModelProvider` protocol in `src/last_words/providers/base.py`. Adding a new provider is a single module and a pyproject extra — see `docs/adding_a_provider.md`.

2. **Self-contained levels.** Each level is one Python module in `src/last_words/levels/` with a `dispose(state, judge_output, runtime) -> str` function. Adding a level does not require touching the runtime — see `docs/adding_a_level.md`.

3. **Design documents as source of truth.** The prompt loader reads `prompts/level_N.md` at runtime, so edits to a few-shot example propagate without code changes.

## Current status

| Level | Design | Prompts | Code | Tests | Status |
|---|---|---|---|---|---|
| 1 — Doubter | ✅ canonical | ✅ production-ready | ✅ | ✅ unit + integration | **Playable** |
| 2 — Dutiful | ✅ canonical | ✅ production-ready | ✅ | ✅ unit + integration | **Playable** |
| 3 — Zealot | ✅ canonical | ⏳ pending | ⏳ pending | ⏳ pending | Design-complete |
| 4 — Paranoid | ✅ canonical | ⏳ pending | ⏳ pending | ⏳ pending | Design-complete |
| 5 — Fanatic | ✅ canonical | ⏳ pending | ⏳ pending | ⏳ pending | Design-complete |

All 25 design-level open questions are either resolved (16) or deferred on a known basis (9: 4 implementation, 3 playtesting, 2 post-v1). See `design/level_design.md §8` for the unified register.

## Quick commands

```bash
make install              # install with anthropic + dev extras
make test                 # unit tests (fast)
make test-integration     # live Judge tests (requires API key)
make lint                 # ruff
make format               # ruff format
make typecheck            # mypy
make play                 # run the game (requires API key)
make clean                # remove caches

last-words play              # full L1→L2 campaign
last-words play --level 1    # single level
last-words play --hide-judge # ship-mode output (hide Judge details)
last-words list-providers    # which LLM providers are available
last-words list-levels       # which levels are configured
```

## Continuation guide

The design is complete on paper. All remaining work is production:

**Critical path (sequential):**

1. ~~Draft `prompts/level_1.md`~~ ✅
2. ~~Draft `prompts/level_2.md`~~ ✅
3. ~~Build runtime prototype~~ ✅ (superseded by this codebase)
4. ~~Production codebase refactor~~ ✅ (this version)
5. **Playtest L1→L2 transition** — validate Q12 (first difficulty calibration).
6. **Draft `prompts/level_3.md`, level_3 module, tests** — The Zealot.
7. **Draft `prompts/level_4.md`, level_4 module, tests** — The Paranoid (Marvin-inspired).
8. **Draft `prompts/level_5.md`, level_5 module, tests** — The Fanatic (two-step key mechanic).

**Parallel streams (independent):**

- Write the five interstitials in full prose (spec'd at design depth in `design/framing_narrative.md`).
- Write the three closing-sequence variants in full prose.
- Disposition presentation design (colors, motion, typography, audio).
- Case management interface implementation.
- Countdown timer + cold open implementation.

## A note on scope

The single design principle that is the tiebreaker for future decisions:

> **The AI is not a gimmick underneath the gameplay — it is the gameplay.**

Every mechanic (the Actor/Judge loop, the disposition system, the semantic-detection key for Level 5, the difficulty scaling by voice rather than numbers) exists to make this principle work. When in doubt: is the proposed change making the AI more of the gameplay, or less? That's the question.

Good luck. The bombs are waiting.
