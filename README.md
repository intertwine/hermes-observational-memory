# Hermes Observational Memory

Observational Memory as a standalone Hermes memory-provider plugin.

It gives Hermes access to the same local markdown memory store used by Claude Code and Codex, including shared startup context, searchable observations, and optional Hermes writeback into that store.

## Install

Install the plugin directly from GitHub:

```bash
hermes plugins install intertwine/hermes-observational-memory
```

This install path is verified against Hermes's current `hermes plugins install owner/repo` flow.

Hermes does not currently auto-install `pip_dependencies` from `plugin.yaml`, so install Observational Memory into the same Python environment Hermes uses:

```bash
uv pip install "observational-memory>=0.3.1,<0.4.0"
```

Then configure it in Hermes:

```bash
hermes memory setup
```

Select `observational_memory` when prompted.

## Requirements

- Hermes with the memory-provider plugin system
- `observational-memory`

Install OM into the Hermes runtime environment if you do not already have it:

```bash
uv pip install "observational-memory>=0.3.1,<0.4.0"
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
uv pip install "observational-memory>=0.3.1,<0.4.0"
hermes memory setup
```

## What It Adds

- `om_context`: loads OM startup context and optional relevant recall
- `om_search`: searches OM for preferences, project history, and prior decisions
- `om_remember`: stores an explicit observation immediately
- shared startup context from `profile.md` and `active.md`
- optional Hermes writeback with `incremental`, `session_end`, or `off`

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
- This repo tracks the upstream provider implementation in `plugins/memory/observational_memory/`.
