# Observational Memory Installed

For Hermes-only use:

```bash
uv pip install "observational-memory>=0.4.1,<0.5.0"
hermes memory setup
```

Choose `observational_memory` in the setup wizard.

If you also want Claude Code and Codex to share the same memory store:

```bash
om install
```

If you already use Observational Memory with Claude Code or Codex, Hermes will share the same memory directory by default.
