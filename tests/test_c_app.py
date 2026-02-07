"""
Tests for Member C — app.py
=============================
Tests the LocalBoltApp UI wiring logic with MOCKED engine.

The engine (BoltEngine) is completely mocked — these tests verify
that Member C's UI layer works correctly in isolation:
  - Widget tree composition
  - Status bar updates
  - Error display
  - State update message handling

All teammate modules are faked so these tests run standalone.
"""

from __future__ import annotations

import sys
import tempfile
import types
from dataclasses import dataclass, field
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from rich.text import Text

from localbolt.ui.widgets import AssemblyView, StatusBar


# ────────────────────────────────────────────────────────────
# Fake state/engine matching main branch interfaces
# ────────────────────────────────────────────────────────────
@dataclass
class FakeInstructionStats:
    latency: int = 1
    uops: float = 0.5
    throughput: float = 0.5


@dataclass
class FakeState:
    source_path: str = ""
    source_code: str = ""
    asm_content: str = "push rbp\nmov rbp, rsp\nret"
    asm_mapping: dict = field(default_factory=dict)
    perf_stats: dict = field(default_factory=dict)
    raw_mca_output: str = ""
    compiler_output: str = ""
    is_dirty: bool = False
    last_update: float = 0.0


class FakeEngine:
    """Mimics BoltEngine from main's engine.py."""

    def __init__(self, source_file: str):
        self.state = FakeState(source_path=source_file)
        self.on_update_callback = None
        self._started = False
        self._refreshed = False

    def start(self):
        self._started = True
        # Trigger the callback as the real engine would on initial compile
        if self.on_update_callback:
            self.on_update_callback(self.state)

    def stop(self):
        pass

    def refresh(self):
        self._refreshed = True
        if self.on_update_callback:
            self.on_update_callback(self.state)


# ────────────────────────────────────────────────────────────
# Inject fake teammate modules into sys.modules
# ────────────────────────────────────────────────────────────
def _inject_fakes(engine_instance=None):
    """
    Inject fake versions of all teammate modules.
    Returns (fakes_dict, cleanup_function).
    """
    # Fake localbolt.engine
    engine_mod = types.ModuleType("localbolt.engine")
    if engine_instance is not None:
        engine_mod.BoltEngine = lambda source_file: engine_instance
    else:
        engine_mod.BoltEngine = FakeEngine

    # Fake localbolt.utils.highlighter
    hl_mod = types.ModuleType("localbolt.utils.highlighter")
    hl_mod.highlight_asm = MagicMock(return_value=Text("push rbp\nmov rbp, rsp\nret"))
    hl_mod.build_gutter = MagicMock(return_value=Text("push rbp\nmov rbp, rsp\nret"))

    # Fake localbolt.parsing.perf_parser
    pp_mod = types.ModuleType("localbolt.parsing.perf_parser")
    pp_mod.InstructionStats = FakeInstructionStats

    # Fake localbolt.utils.state
    state_mod = types.ModuleType("localbolt.utils.state")
    state_mod.LocalBoltState = FakeState

    # Fake localbolt.utils.watcher
    watcher_mod = types.ModuleType("localbolt.utils.watcher")

    # Ensure parent package modules exist
    fakes = {
        "localbolt.engine": engine_mod,
        "localbolt.utils.highlighter": hl_mod,
        "localbolt.utils.state": state_mod,
        "localbolt.utils.watcher": watcher_mod,
        "localbolt.parsing.perf_parser": pp_mod,
    }

    originals = {}
    for name, mod in fakes.items():
        originals[name] = sys.modules.get(name)
        sys.modules[name] = mod

    def cleanup():
        for name in fakes:
            if originals[name] is None:
                sys.modules.pop(name, None)
            else:
                sys.modules[name] = originals[name]

    return fakes, cleanup


# ────────────────────────────────────────────────────────────
# Helper: create a temp .cpp file
# ────────────────────────────────────────────────────────────
def _make_tmp_cpp(content: str = "int main() { return 0; }\n") -> str:
    f = tempfile.NamedTemporaryFile(mode="w", suffix=".cpp", delete=False)
    f.write(content)
    f.flush()
    f.close()
    return f.name


# ────────────────────────────────────────────────────────────
# App composition tests
# ────────────────────────────────────────────────────────────
class TestAppComposition:
    """Verify the widget tree is assembled correctly."""

    @pytest.mark.asyncio
    async def test_app_has_assembly_view(self):
        tmp = _make_tmp_cpp()
        fakes, cleanup = _inject_fakes()
        try:
            from localbolt.ui.app import LocalBoltApp
            app = LocalBoltApp(source_file=tmp)
            async with app.run_test(size=(120, 40)) as pilot:
                av = pilot.app.query_one("#assembly-view", AssemblyView)
                assert av is not None
        finally:
            cleanup()
            Path(tmp).unlink(missing_ok=True)

    @pytest.mark.asyncio
    async def test_app_has_status_bar(self):
        tmp = _make_tmp_cpp()
        fakes, cleanup = _inject_fakes()
        try:
            from localbolt.ui.app import LocalBoltApp
            app = LocalBoltApp(source_file=tmp)
            async with app.run_test(size=(120, 40)) as pilot:
                sb = pilot.app.query_one("#status-bar", StatusBar)
                assert sb is not None
        finally:
            cleanup()
            Path(tmp).unlink(missing_ok=True)

    @pytest.mark.asyncio
    async def test_app_has_no_source_view(self):
        """SourceView should NOT be in the widget tree (assembly-only UI)."""
        tmp = _make_tmp_cpp()
        fakes, cleanup = _inject_fakes()
        try:
            from localbolt.ui.app import LocalBoltApp
            app = LocalBoltApp(source_file=tmp)
            async with app.run_test(size=(120, 40)) as pilot:
                results = pilot.app.query("#source-view")
                assert len(results) == 0
        finally:
            cleanup()
            Path(tmp).unlink(missing_ok=True)


# ────────────────────────────────────────────────────────────
# App init tests
# ────────────────────────────────────────────────────────────
class TestAppInit:
    """Verify constructor stores values correctly."""

    def test_stores_source_file(self):
        from localbolt.ui.app import LocalBoltApp
        app = LocalBoltApp(source_file="/tmp/test.cpp")
        assert app.source_file.endswith("test.cpp")

    def test_engine_starts_none(self):
        from localbolt.ui.app import LocalBoltApp
        app = LocalBoltApp(source_file="/tmp/test.cpp")
        assert app.engine is None


# ────────────────────────────────────────────────────────────
# Engine integration tests (mocked engine)
# ────────────────────────────────────────────────────────────
class TestEngineIntegration:
    """Test that the app correctly wires up to BoltEngine."""

    @pytest.mark.asyncio
    async def test_engine_is_started_on_mount(self):
        """The engine should be started when the app mounts."""
        tmp = _make_tmp_cpp()
        engine = FakeEngine(tmp)
        fakes, cleanup = _inject_fakes(engine_instance=engine)
        try:
            from localbolt.ui.app import LocalBoltApp
            app = LocalBoltApp(source_file=tmp)
            async with app.run_test(size=(120, 40)) as pilot:
                await pilot.pause()
                assert engine._started
        finally:
            cleanup()
            Path(tmp).unlink(missing_ok=True)

    @pytest.mark.asyncio
    async def test_status_shows_ready_after_update(self):
        """After engine state update, status should be 'ready'."""
        tmp = _make_tmp_cpp()
        engine = FakeEngine(tmp)
        fakes, cleanup = _inject_fakes(engine_instance=engine)
        try:
            from localbolt.ui.app import LocalBoltApp
            app = LocalBoltApp(source_file=tmp)
            async with app.run_test(size=(120, 40)) as pilot:
                await pilot.pause()
                sb = pilot.app.query_one("#status-bar", StatusBar)
                assert sb._status == "ready"
                assert sb._errors == 0
        finally:
            cleanup()
            Path(tmp).unlink(missing_ok=True)

    @pytest.mark.asyncio
    async def test_compiler_error_shows_error_status(self):
        """When compiler_output contains 'error', status should be 'error'."""
        tmp = _make_tmp_cpp()
        engine = FakeEngine(tmp)
        engine.state.compiler_output = "fatal error: file not found"
        fakes, cleanup = _inject_fakes(engine_instance=engine)
        try:
            from localbolt.ui.app import LocalBoltApp
            app = LocalBoltApp(source_file=tmp)
            async with app.run_test(size=(120, 40)) as pilot:
                await pilot.pause()
                sb = pilot.app.query_one("#status-bar", StatusBar)
                assert sb._status == "error"
                assert sb._errors == 1
        finally:
            cleanup()
            Path(tmp).unlink(missing_ok=True)

    @pytest.mark.asyncio
    async def test_assembly_view_gets_content(self):
        """After a state update, the assembly view should have content."""
        tmp = _make_tmp_cpp()
        engine = FakeEngine(tmp)
        engine.state.asm_content = "push rbp\nmov rbp, rsp\npop rbp\nret"
        fakes, cleanup = _inject_fakes(engine_instance=engine)
        try:
            from localbolt.ui.app import LocalBoltApp
            app = LocalBoltApp(source_file=tmp)
            async with app.run_test(size=(120, 40)) as pilot:
                await pilot.pause()
                # Highlighter was called
                hl = fakes["localbolt.utils.highlighter"]
                assert hl.build_gutter.called or hl.highlight_asm.called
        finally:
            cleanup()
            Path(tmp).unlink(missing_ok=True)

    @pytest.mark.asyncio
    async def test_action_refresh_calls_engine(self):
        """Pressing 'r' should call engine.refresh()."""
        tmp = _make_tmp_cpp()
        engine = FakeEngine(tmp)
        fakes, cleanup = _inject_fakes(engine_instance=engine)
        try:
            from localbolt.ui.app import LocalBoltApp
            app = LocalBoltApp(source_file=tmp)
            async with app.run_test(size=(120, 40)) as pilot:
                await pilot.pause()
                engine._refreshed = False  # reset after initial
                await pilot.press("r")
                await pilot.pause()
                assert engine._refreshed
        finally:
            cleanup()
            Path(tmp).unlink(missing_ok=True)

    @pytest.mark.asyncio
    async def test_engine_failure_shows_error(self):
        """If engine import fails, the app should show an error gracefully."""
        tmp = _make_tmp_cpp()
        # Don't inject engine fake — let the import fail
        engine_mod = types.ModuleType("localbolt.engine")

        def bad_engine(source_file):
            raise RuntimeError("Engine not available")

        engine_mod.BoltEngine = bad_engine
        originals = {
            "localbolt.engine": sys.modules.get("localbolt.engine"),
        }
        sys.modules["localbolt.engine"] = engine_mod
        try:
            from localbolt.ui.app import LocalBoltApp
            app = LocalBoltApp(source_file=tmp)
            async with app.run_test(size=(120, 40)) as pilot:
                await pilot.pause()
                sb = pilot.app.query_one("#status-bar", StatusBar)
                assert sb._status == "error"
        finally:
            if originals["localbolt.engine"] is None:
                sys.modules.pop("localbolt.engine", None)
            else:
                sys.modules["localbolt.engine"] = originals["localbolt.engine"]
            Path(tmp).unlink(missing_ok=True)


# ────────────────────────────────────────────────────────────
# run_tui function test
# ────────────────────────────────────────────────────────────
class TestRunTui:
    """Test the run_tui entry point."""

    def test_run_tui_creates_app(self):
        """run_tui should create a LocalBoltApp and call run()."""
        with patch("localbolt.ui.app.LocalBoltApp") as MockApp:
            mock_instance = MagicMock()
            MockApp.return_value = mock_instance
            from localbolt.ui.app import run_tui
            run_tui("/tmp/test.cpp")
            MockApp.assert_called_once_with("/tmp/test.cpp")
            mock_instance.run.assert_called_once()
