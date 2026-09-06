# Legacy status and removal

September 5, 2026. Version 1.5.2 is the final, unmaintained release. No future
feature, compatibility or security fixes are promised. Source and existing
licenses remain available for forks. This does not disable other users' plugins.

1. Back up OM data and configuration privately. Preserve native Hermes
   `MEMORY.md` and `USER.md`; they are not owned by this plugin.
2. In each affected `HERMES_HOME`, run `hermes memory setup` and select built-in
   memory. Then disable/remove the `observational_memory` plugin with the host's
   plugin commands. A provider selection and a plugin enabled-list are separate.
3. Remove any legacy link under the Hermes source tree's `plugins/memory/` that
   points to this plugin. Remove only OM entries, never the entire plugins folder.
4. Restart the affected gateway/sessions and inspect `hermes memory status`.
   Verify native memory is enabled and OM is no longer selected or discovered.
5. Remove separately installed OM services/packages only after checking consumers.

See the [core migration guide](https://github.com/intertwine/observational-memory/blob/main/docs/legacy-migration.md)
for archive preservation, core hooks, multiple installs, sync/relay retirement
and native-memory limits. A fallback to raw materialized memory after policy
failure is deliberately removed in 1.5.2; explicit historical retrieval remains
distinct from automatic startup context. Tests use a fake Hermes provider API,
not a claim that every future Hermes version is compatible.
