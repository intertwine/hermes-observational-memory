# Hermes Observational Memory

Observational Memory as a standalone Hermes memory-provider plugin.

It gives Hermes access to the same local-first memory store used by Claude Code, Codex, Grok, Cowork, and other OM-connected agents. Hermes can load compact startup context, search prior observations and reflections, store explicit notes, and optionally write Hermes turns back into Observational Memory.

## Why Observational Memory

Observational Memory is a local-first memory backend. Memory stays in readable markdown files, with optional OM Cluster sync for sharing trusted records across machines. That makes it a good fit when you want cross-agent continuity without turning memory into an opaque hosted service.

Compared with hosted memory providers, this plugin is more inspectable and easier to audit. Compared with graph or hierarchy-first providers, it is focused on stable session continuity: an observer writes durable observations, a reflector condenses them into compact startup memory, and Hermes can recall more detail on demand.

## Requirements

- Hermes with user-installed memory provider discovery. This is present in Hermes `v2026.4.16` and newer.
- `observational-memory>=0.6.3,<0.7`.
- Optional: an initialized OM Cluster if you want Hermes to share memory across machines.

## Install

Install the plugin from GitHub:

```bash
hermes plugins install intertwine/hermes-observational-memory --no-enable
```

Memory providers are `kind: exclusive` plugins. They are activated through `memory.provider`, not through `plugins.enabled`, so `--no-enable` is intentional.

Then configure Hermes:

```bash
hermes memory setup
```

Select `observational_memory`.

Hermes will install the declared Python dependency during setup when it is missing. If you need to install it manually in the Hermes runtime, run:

```bash
uv pip install "observational-memory>=0.6.3,<0.7"
```

If you also want Claude Code, Codex, Grok, or Cowork to use the same OM store, run:

```bash
om install --all --non-interactive
```

## What It Adds

Tools:

- `om_context`: load compact startup context, with optional query-specific recall.
- `om_search`: search OM observations and reflections.
- `om_remember`: store an explicit observation immediately.

Memory integration:

- shared startup context from `profile.md` and `active.md`;
- optional Hermes session writeback with `incremental`, `session_end`, or `off`;
- best-effort OM Cluster pull-before-context when OM Cluster is enabled and `sync_before_context` is true;
- cluster-aware `om_remember`, so explicit Hermes notes become signed OM Cluster observation records instead of editing generated markdown directly.

## OM Cluster

OM Cluster stays opt-in. The plugin only syncs when the local OM install is already initialized, enabled, and configured for startup pull.

To verify cluster state:

```bash
om cluster status
om cluster sync
```

To have Hermes pull shared records before reading startup memory, set `sync_before_context = true` in OM's cluster config or use:

```bash
OM_CLUSTER_SYNC_BEFORE_CONTEXT=1 hermes
```

The pull is best-effort and deadline-bound by OM's `startup_pull_deadline_ms`, so disabled, absent, or temporarily unreachable cluster transports do not block normal Hermes startup.

## Config

Plugin config file:

```text
$HERMES_HOME/observational_memory.json
```

| Key | Default | Description |
| --- | --- | --- |
| `llm_provider` | `inherit-existing` | Hermes-side writeback provider: `inherit-existing`, `anthropic`, or `openai`. |
| `llm_model` | `""` | Optional observer/reflector model override. |
| `memory_dir` | `~/.local/share/observational-memory` | Shared OM memory directory. |
| `env_file` | `~/.config/observational-memory/env` | OM env file path. |
| `search_backend` | `bm25` | Search backend: `bm25`, `qmd`, `qmd-hybrid`, or `none`. |
| `writeback_mode` | `incremental` | `incremental`, `session_end`, or `off`. |

Optional secret written to Hermes `.env`:

| Env var | Purpose |
| --- | --- |
| `OM_HERMES_API_KEY` | API key for a selected direct writeback provider. |

## Validation

Local plugin tests:

```bash
uv run --with pytest pytest tests -q
```

Runtime smoke path:

```bash
hermes memory status
om doctor --validate-key
om cluster status
```

In a Hermes session, ask Hermes to use:

- `om_context` for startup context;
- `om_search` for a known memory query;
- `om_remember` for a test note, then confirm it appears through `om search`.

## Notes

- The installed plugin name is `observational_memory`, even though the GitHub repo is named `hermes-observational-memory`.
- Supported Hermes versions discover this plugin from `$HERMES_HOME/plugins/observational_memory`; no source-tree symlink is required.
- Older Hermes builds that only scan `plugins/memory/` are not supported by this release path. Upgrade Hermes instead of adding the old symlink workaround.
