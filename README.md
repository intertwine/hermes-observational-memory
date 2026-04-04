# Hermes Observational Memory

Observational Memory as a standalone Hermes memory-provider plugin.

It gives Hermes access to the same local markdown memory store used by Claude Code and Codex, including shared startup context, searchable observations, and optional Hermes writeback into that store.

As of `observational-memory` 0.4.1, the package includes a dedicated Hermes transcript parser that filters v0.7.0 JSONL session logs to human-meaningful content (user/assistant prose only, tool calls summarized as one-liners), achieving ~19x noise reduction on typical sessions.

## Why Observational Memory

Observational Memory is a local-first memory backend for Hermes that keeps memory in plain markdown and can share that same store with Claude Code and Codex. Instead of treating memory as a remote fact database or relying entirely on per-turn dynamic retrieval, it derives compact startup context from longer-term observations and reflections, then lets Hermes search or write into that shared store when needed.

### Where It Fits

- Best fit if you want cross-agent continuity, local files, and inspectable memory instead of a hosted memory service.
- Compared with Honcho, Mem0, and RetainDB, this is much more local and transparent, with less SaaS or black-box behavior.
- Compared with OpenViking, Hindsight, and ByteRover, this is less about hierarchical browsing or graph-style knowledge management, and more about stable session continuity plus compact startup context.
- Compared with Holographic, this is less of a local fact database with algebraic retrieval and more of a shared observation layer across multiple agent tools.

### Architectural Basis

The underlying `observational-memory` package adapts [Mastra's Observational Memory approach](https://mastra.ai/research/observational-memory): an Observer and Reflector compress conversation history into a stable observation log and compact startup memory, rather than depending only on turn-by-turn retrieval. That makes the resulting context more predictable and prompt-cache-friendly while keeping the memory store readable on disk.

Mastra reports 84.23% on LongMemEval with `gpt-4o` and 94.87% with `gpt-5-mini` for the underlying Observational Memory architecture. Those benchmark results are for Mastra's OM approach itself, not for this standalone Hermes plugin, but they are a strong reason to bring the same pattern into Hermes.

## Install

Install the plugin directly from GitHub:

```bash
hermes plugins install intertwine/hermes-observational-memory
```

This install path is verified against Hermes's current `hermes plugins install owner/repo` flow.

Hermes does not currently auto-install `pip_dependencies` from `plugin.yaml`, so install Observational Memory into the same Python environment Hermes uses:

```bash
uv pip install "observational-memory>=0.4.1,<0.5.0"
```

Then configure it in Hermes:

```bash
hermes memory setup
```

Select `observational_memory` when prompted.

## Requirements

- Hermes with the memory-provider plugin system
- `observational-memory` >= 0.4.1 (includes Hermes transcript parser)

Install OM into the Hermes runtime environment if you do not already have it:

```bash
uv pip install "observational-memory>=0.4.1,<0.5.0"
```

If you also want Claude Code and Codex to share the same memory store, run:

```bash
om install
```

`om install` is optional for Hermes-only use.

For Hermes writeback, either use an existing OM config or set a direct Anthropic/OpenAI key during `hermes memory setup`.

## Manual Install

If you prefer cloning manually:

```bash
git clone https://github.com/intertwine/hermes-observational-memory.git \
  ~/.hermes/plugins/observational_memory
```

Then:

```bash
uv pip install "observational-memory>=0.4.1,<0.5.0"
hermes memory setup
```

## What It Adds

**Tools:**
- `om_context`: loads OM startup context and optional relevant recall
- `om_search`: searches OM for preferences, project history, and prior decisions
- `om_remember`: stores an explicit observation immediately

**Memory integration:**
- shared startup context from `profile.md` and `active.md`
- optional Hermes writeback with `incremental`, `session_end`, or `off`
- Hermes session log parser (via `observational-memory` 0.4.1+) for cron-based observation extraction from JSONL session logs

## Config

Config file: `$HERMES_HOME/observational_memory.json`

| Key | Default | Description |
|-----|---------|-------------|
| `llm_provider` | `inherit-existing` | Hermes-side writeback provider: `inherit-existing`, `anthropic`, or `openai` |
| `llm_model` | `""` | Optional observer/reflector model override |
| `memory_dir` | `~/.local/share/observational-memory` | Shared OM markdown memory directory |
| `env_file` | `~/.config/observational-memory/env` | OM env file path |
| `search_backend` | `bm25` | Search backend: `bm25`, `qmd`, `qmd-hybrid`, `none` |
| `writeback_mode` | `incremental` | `incremental`, `session_end`, or `off` |

Optional secret written to Hermes `.env`:

| Env var | Purpose |
|---------|---------|
| `OM_HERMES_API_KEY` | API key for the selected direct writeback provider |

## Validation

This repository ships standalone tests for the provider behavior. Run them with:

```bash
uv run --with pytest pytest tests -q
```

## Notes

- This repository is laid out as a Hermes directory plugin, so the repo root is the plugin root.
- The installed plugin name is `observational_memory`, even though the GitHub repo is named `hermes-observational-memory`.
- Hermes currently clones directory plugins from Git but does not install their Python dependencies automatically, so the `uv pip install` step is still required.
