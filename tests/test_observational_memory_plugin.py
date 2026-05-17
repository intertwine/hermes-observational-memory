from __future__ import annotations

import importlib.util
import json
import sys
import threading
import types
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _load_plugin_module(monkeypatch):
    agent_pkg = types.ModuleType("agent")
    memory_provider_mod = types.ModuleType("agent.memory_provider")

    class MemoryProvider:
        pass

    memory_provider_mod.MemoryProvider = MemoryProvider
    monkeypatch.setitem(sys.modules, "agent", agent_pkg)
    monkeypatch.setitem(sys.modules, "agent.memory_provider", memory_provider_mod)

    module_name = "standalone_observational_memory_plugin"
    sys.modules.pop(module_name, None)
    spec = importlib.util.spec_from_file_location(module_name, ROOT / "__init__.py")
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def _install_fake_om(monkeypatch, tmp_path, plugin_module):
    fake_pkg = types.ModuleType("observational_memory")
    fake_pkg.__path__ = []
    original_find_spec = importlib.util.find_spec

    reindex_calls = []
    observer_calls = []

    @dataclass
    class FakeConfig:
        memory_dir: Path | None = None
        env_file: Path | None = None
        llm_provider: str = "auto"
        llm_model: str | None = None
        search_backend: str = "bm25"
        min_messages: int = 5

        def __post_init__(self):
            self.memory_dir = (self.memory_dir or (tmp_path / "memory")).expanduser()
            self.env_file = (self.env_file or (tmp_path / "env")).expanduser()

        @property
        def observations_path(self) -> Path:
            return self.memory_dir / "observations.md"

        @property
        def reflections_path(self) -> Path:
            return self.memory_dir / "reflections.md"

        @property
        def profile_path(self) -> Path:
            return self.memory_dir / "profile.md"

        @property
        def active_path(self) -> Path:
            return self.memory_dir / "active.md"

        def ensure_memory_dir(self) -> None:
            self.memory_dir.mkdir(parents=True, exist_ok=True)

        def load_env_file(self) -> None:
            return None

        def validate_provider_config(self, provider=None):
            return "anthropic"

    class FakeResult:
        def __init__(self, rank, score, source, heading, content):
            self.rank = rank
            self.score = score
            self.document = types.SimpleNamespace(
                source=types.SimpleNamespace(value=source),
                heading=heading,
                content=content,
            )

    class FakeBackend:
        def is_ready(self):
            return True

        def search(self, query, limit=10):
            return [
                FakeResult(
                    1,
                    9.5,
                    "reflections",
                    "## Active Projects",
                    "## Active Projects\nHermes and Codex both use the same memory store.",
                )
            ][:limit]

    def get_backend(name, config):
        return FakeBackend()

    def reindex(config):
        reindex_calls.append(config.memory_dir)
        return 1

    def ensure_startup_memory(config):
        config.ensure_memory_dir()
        config.profile_path.write_text(
            "# Startup Profile\n\n- prefers concise output\n"
        )
        config.active_path.write_text(
            "# Active Context\n\n- shipping a Hermes memory provider\n"
        )

    def refresh_startup_memory(config):
        ensure_startup_memory(config)

    @dataclass
    class Message:
        role: str
        content: str
        timestamp: str
        source: str

    def run_observer(messages, config, dry_run=False):
        observer_calls.append(list(messages))
        config.ensure_memory_dir()
        config.observations_path.write_text(
            "# Observations\n\n## 2026-04-03\n\n### Observations\n- 🔴 12:00 Observed Hermes sync\n"
        )
        return "ok"

    config_mod = types.ModuleType("observational_memory.config")
    config_mod.Config = FakeConfig

    search_mod = types.ModuleType("observational_memory.search")
    search_mod.get_backend = get_backend
    search_mod.reindex = reindex

    startup_mod = types.ModuleType("observational_memory.startup_memory")
    startup_mod.ensure_startup_memory = ensure_startup_memory
    startup_mod.refresh_startup_memory = refresh_startup_memory

    transcripts_mod = types.ModuleType("observational_memory.transcripts")
    transcripts_mod.Message = Message

    observe_mod = types.ModuleType("observational_memory.observe")
    observe_mod.run_observer = run_observer

    monkeypatch.setitem(sys.modules, "observational_memory", fake_pkg)
    monkeypatch.setitem(sys.modules, "observational_memory.config", config_mod)
    monkeypatch.setitem(sys.modules, "observational_memory.search", search_mod)
    monkeypatch.setitem(sys.modules, "observational_memory.startup_memory", startup_mod)
    monkeypatch.setitem(
        sys.modules, "observational_memory.transcripts", transcripts_mod
    )
    monkeypatch.setitem(sys.modules, "observational_memory.observe", observe_mod)
    monkeypatch.setattr(
        plugin_module.importlib.util,
        "find_spec",
        lambda name: (
            object() if name == "observational_memory" else original_find_spec(name)
        ),
    )

    return reindex_calls, observer_calls


def _install_fake_cluster(
    monkeypatch,
    *,
    enabled=True,
    sync_before_context=True,
    sync_on_observe=False,
):
    state = {"sync_calls": [], "records": [], "materialized": []}

    cluster_config = types.SimpleNamespace(
        sync_before_context=sync_before_context,
        startup_pull_deadline_ms=37,
        sync_on_observe=sync_on_observe,
        default_namespace="shared",
        node_alias="node-a",
    )

    def cluster_feature_enabled(config):
        return enabled

    def load_cluster_config(config):
        return cluster_config

    def sync_cluster(config, **kwargs):
        state["sync_calls"].append(kwargs)
        return types.SimpleNamespace(pulled=0, pushed=0, materialized=False)

    def materialize_cluster_memory(config, store):
        state["materialized"].append(store)
        return types.SimpleNamespace(any_written=True)

    def namespace_for_event(config, source_event):
        return "shared"

    def source_metadata(*, config, cluster_config, source):
        return {"agent": source, "host_alias": cluster_config.node_alias}

    class FakeStore:
        cluster_config = types.SimpleNamespace(node_alias="node-a")

        @classmethod
        def from_config(cls, config):
            return cls()

        def append_record(self, **kwargs):
            state["records"].append(kwargs)
            return types.SimpleNamespace(record_id=f"record-{len(state['records'])}")

    sync_pkg = types.ModuleType("observational_memory.sync")
    sync_pkg.__path__ = []

    config_mod = types.ModuleType("observational_memory.sync.config")
    config_mod.cluster_feature_enabled = cluster_feature_enabled
    config_mod.load_cluster_config = load_cluster_config

    engine_mod = types.ModuleType("observational_memory.sync.engine")
    engine_mod.sync_cluster = sync_cluster

    materialize_mod = types.ModuleType("observational_memory.sync.materialize")
    materialize_mod.materialize_cluster_memory = materialize_cluster_memory

    source_mod = types.ModuleType("observational_memory.sync.source")
    source_mod.namespace_for_event = namespace_for_event
    source_mod.source_metadata = source_metadata

    store_mod = types.ModuleType("observational_memory.sync.store")
    store_mod.ClusterStore = FakeStore

    monkeypatch.setitem(sys.modules, "observational_memory.sync", sync_pkg)
    monkeypatch.setitem(sys.modules, "observational_memory.sync.config", config_mod)
    monkeypatch.setitem(sys.modules, "observational_memory.sync.engine", engine_mod)
    monkeypatch.setitem(
        sys.modules, "observational_memory.sync.materialize", materialize_mod
    )
    monkeypatch.setitem(sys.modules, "observational_memory.sync.source", source_mod)
    monkeypatch.setitem(sys.modules, "observational_memory.sync.store", store_mod)

    return state


def test_system_prompt_includes_startup_memory(monkeypatch, tmp_path):
    plugin_module = _load_plugin_module(monkeypatch)
    _install_fake_om(monkeypatch, tmp_path, plugin_module)
    provider = plugin_module.ObservationalMemoryProvider()
    provider.initialize("session-1", hermes_home=str(tmp_path))

    prompt = provider.system_prompt_block()

    assert "Observational Memory" in prompt
    assert "Startup Profile" in prompt
    assert "Active Context" in prompt


def test_system_prompt_pulls_cluster_before_context(monkeypatch, tmp_path):
    plugin_module = _load_plugin_module(monkeypatch)
    _install_fake_om(monkeypatch, tmp_path, plugin_module)
    cluster = _install_fake_cluster(monkeypatch)
    provider = plugin_module.ObservationalMemoryProvider()
    provider.initialize("session-1-cluster", hermes_home=str(tmp_path))

    cluster["sync_calls"].clear()
    provider.system_prompt_block()

    assert cluster["sync_calls"] == [{"deadline_ms": 37, "pull_only": True}]


def test_om_remember_appends_local_observation(monkeypatch, tmp_path):
    plugin_module = _load_plugin_module(monkeypatch)
    reindex_calls, _ = _install_fake_om(monkeypatch, tmp_path, plugin_module)
    provider = plugin_module.ObservationalMemoryProvider()
    provider.initialize("session-2", hermes_home=str(tmp_path))

    result = json.loads(
        provider.handle_tool_call(
            "om_remember",
            {
                "content": "Bryan wants fixes grounded in artifacts",
                "importance": "high",
            },
        )
    )

    obs = provider._config.observations_path.read_text()
    assert result["stored"] is True
    assert "Bryan wants fixes grounded in artifacts" in obs
    assert "🔴" in obs
    assert reindex_calls


def test_om_remember_writes_cluster_record_when_enabled(monkeypatch, tmp_path):
    plugin_module = _load_plugin_module(monkeypatch)
    _install_fake_om(monkeypatch, tmp_path, plugin_module)
    cluster = _install_fake_cluster(monkeypatch, sync_on_observe=True)
    provider = plugin_module.ObservationalMemoryProvider()
    provider.initialize("session-2-cluster", hermes_home=str(tmp_path))

    cluster["sync_calls"].clear()
    result = json.loads(
        provider.handle_tool_call(
            "om_remember",
            {
                "content": "Hermes should see shared cluster memory",
                "importance": "high",
            },
        )
    )

    assert result["stored"] is True
    assert result["cluster_record_id"] == "record-1"
    assert cluster["materialized"]
    assert cluster["sync_calls"] == [{"deadline_ms": 1500}]
    record = cluster["records"][0]
    assert record["kind"] == "observation"
    assert record["namespace"] == "shared"
    assert record["source"]["agent"] == "hermes"
    assert "Hermes should see shared cluster memory" in record["payload"]["body"]
    assert record["payload"]["retention"] == "manual"


def test_incremental_sync_flushes_to_observer(monkeypatch, tmp_path):
    plugin_module = _load_plugin_module(monkeypatch)
    _, observer_calls = _install_fake_om(monkeypatch, tmp_path, plugin_module)
    provider = plugin_module.ObservationalMemoryProvider()
    provider.initialize("session-3", hermes_home=str(tmp_path))
    provider._config.min_messages = 5

    provider.sync_turn("first user", "first assistant")
    provider.sync_turn("second user", "second assistant")
    provider.sync_turn("third user", "third assistant")
    provider.shutdown()

    assert observer_calls
    assert len(observer_calls[0]) == 6
    assert {msg.source for msg in observer_calls[0]} == {"hermes"}


def test_session_end_defers_final_flush_until_active_sync_finishes(
    monkeypatch, tmp_path, caplog
):
    plugin_module = _load_plugin_module(monkeypatch)
    _install_fake_om(monkeypatch, tmp_path, plugin_module)
    provider = plugin_module.ObservationalMemoryProvider()
    provider.initialize("session-4", hermes_home=str(tmp_path))

    flush_calls = []
    released = threading.Event()
    flushed = threading.Event()

    class FakeThread:
        def __init__(self):
            self._alive = True
            self.join_calls = []

        def is_alive(self):
            return self._alive

        def join(self, timeout=None):
            self.join_calls.append(timeout)
            if timeout is None:
                released.wait(timeout=1.0)
                self._alive = False

    def _flush_pending(*, force: bool):
        flush_calls.append(force)
        flushed.set()

    active_thread = FakeThread()
    provider._sync_thread = active_thread
    monkeypatch.setattr(provider, "_flush_pending", _flush_pending)

    with caplog.at_level("WARNING"):
        provider.on_session_end([])

    followup = provider._sync_thread
    assert followup is not active_thread
    assert followup is not None
    assert "deferring final session flush" in caplog.text

    released.set()
    followup.join(timeout=1.0)

    assert flushed.wait(timeout=1.0)
    assert flush_calls == [True]
    assert active_thread.join_calls == [10.0, None]
