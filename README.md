# Hermes Observational Memory

Observational Memory as a standalone Hermes memory-provider plugin.

It gives Hermes access to the same local markdown memory store used by Claude Code and Codex, including shared startup context, searchable observations, and optional Hermes writeback into that store.

## Install

Install the plugin directly from GitHub:

```bash
hermes plugins install intertwine/hermes-observational-memory
```

Then configure it in Hermes:

```bash
hermes memory setup
```

Select `observational_memory` when prompted.

## Requirements

- Hermes with the memory-provider plugin system
- `observational-memory`

Install OM if you do not already have it:

```bash
pip install observational-memory
```

If you want Claude Code and Codex to share the same memory store too, run:

```bash
om install
```

For Hermes writeback, either use an existing OM config or set a direct Anthropic/OpenAI key during `hermes memory setup`.

## Manual Install

If you prefer cloning manually:

```bash
git clone https://github.com/intertwine/hermes-observational-memory.git \
  ~/.hermes/plugins/observational_memory
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

## Notes

- This repository is laid out as a Hermes directory plugin, so the repo root is the plugin root.
- The installed plugin name is `observational_memory`, even though the GitHub repo is named `hermes-observational-memory`.
- This repo mirrors the provider implementation proposed in the Hermes PR adding Observational Memory as a first-class memory provider.
