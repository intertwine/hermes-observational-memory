# Observational Memory Installed

This is a Hermes memory provider, so activation happens through `hermes memory setup`, not `hermes plugins enable`.

```bash
hermes memory setup
```

Select `observational_memory`.

Hermes will install `observational-memory>=0.9.0,<0.10` during setup when it is missing. If you need to install it manually in the Hermes runtime:

```bash
uv pip install "observational-memory>=0.9.0,<0.10"
```

Useful checks:

```bash
hermes memory status
om doctor --validate-key
om cluster status
```

If OM Cluster is enabled and `sync_before_context` is true, Hermes pulls shared records before loading startup memory. No source-tree symlink is required on supported Hermes releases.

OM 0.9.0 usage budgets and bounded observer behavior apply to Hermes writeback. If a hard cap blocks observe or reflection, the plugin logs the block and skips that write without crashing the Hermes session. OpenAI Batch reflection is intentionally disabled for this interactive hook path.
