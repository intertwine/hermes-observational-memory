# Observational Memory Installed

For Hermes-only use:

```bash
uv pip install "observational-memory>=0.5.0,<0.6.0"
ln -s ~/.hermes/plugins/observational_memory \
      ~/.hermes/hermes-agent/plugins/memory/observational_memory
hermes memory setup
```

Choose `observational_memory` in the setup wizard.

For best results, also set up the background reflector (condenses observations into long-term memory daily):

```bash
om install --scheduler auto
```

If you also want Claude Code and Codex to share the same memory store, `om install` handles that too.

If you already use Observational Memory with Claude Code or Codex, Hermes will share the same memory directory by default.

If you enable QMD-backed search in OM, `om status` and `om doctor` now show the search backend and readiness checks directly.
