from __future__ import annotations

import sys
import types


agent_pkg = types.ModuleType("agent")
memory_provider_mod = types.ModuleType("agent.memory_provider")


class MemoryProvider:
    pass


memory_provider_mod.MemoryProvider = MemoryProvider
sys.modules.setdefault("agent", agent_pkg)
sys.modules.setdefault("agent.memory_provider", memory_provider_mod)
