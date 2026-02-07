"""
Member C — Main Textual Application
====================================
Assembly-only viewer with live recompilation on file save.

Integrates with main branch architecture:
  - BoltEngine (engine.py) handles compile → parse → analyze pipeline
  - LocalBoltState holds all application data
  - FileWatcher (utils/watcher.py) detects file saves
  - highlight_asm / build_gutter (utils/highlighter.py) for rendering

The user edits their C++ file in their own IDE; saves are detected
and the assembly view updates automatically.
"""

from __future__ import annotations

from pathlib import Path

from textual.app import App, ComposeResult
from textual.widgets import Header, Footer
from textual.message import Message

from localbolt.ui.widgets import AssemblyView, StatusBar


class LocalBoltApp(App):
    """LocalBolt — a local Compiler Explorer in your terminal."""

    CSS_PATH = "styles.tcss"
    TITLE = "LocalBolt"

    from textual.binding import Binding
    BINDINGS = [
        Binding("q", "quit", "Quit", show=True),
        Binding("r", "refresh", "Recompile", show=True),
    ]

    class StateUpdated(Message):
        """Posted by the engine callback when a recompile finishes."""
        def __init__(self, state) -> None:
            super().__init__()
            self.state = state

    def __init__(self, source_file: str) -> None:
        super().__init__()
        self.source_file: str = str(Path(source_file).resolve())
        self.engine = None  # Will be set in on_mount if engine is available

    # -- compose the widget tree ----------------------------------

    def compose(self) -> ComposeResult:
        yield Header()
        yield AssemblyView()
        yield StatusBar()
        yield Footer()

    # -- lifecycle ------------------------------------------------

    def on_mount(self) -> None:
        self.status_bar.set_status(
            file=Path(self.source_file).name,
            status="starting",
        )
        # Try to import and start the engine (main branch's BoltEngine)
        try:
            from localbolt.engine import BoltEngine
            self.engine = BoltEngine(self.source_file)
            self.engine.on_update_callback = (
                lambda state: self.post_message(self.StateUpdated(state))
            )
            self.engine.start()
            self.status_bar.set_status(status="watching")
            self.notify(f"Monitoring {self.source_file}")
        except Exception as exc:
            self._show_error(f"Engine init error: {exc}")

    def on_unmount(self) -> None:
        if self.engine is not None:
            try:
                self.engine.stop()
            except Exception:
                pass

    # -- convenience accessors ------------------------------------

    @property
    def assembly_view(self) -> AssemblyView:
        return self.query_one("#assembly-view", AssemblyView)

    @property
    def status_bar(self) -> StatusBar:
        return self.query_one("#status-bar", StatusBar)

    # -- handle engine state updates ------------------------------

    def on_local_bolt_app_state_updated(self, message: StateUpdated) -> None:
        """Called when BoltEngine finishes a compile/parse cycle."""
        state = message.state

        # Render the assembly
        try:
            from localbolt.utils.highlighter import highlight_asm, build_gutter
            from localbolt.parsing.perf_parser import InstructionStats

            asm_lines = state.asm_content.splitlines() if state.asm_content else []

            if asm_lines:
                # build_gutter returns a combined Rich Text with highlighting + cycles
                cycle_counts = {}
                for idx, stats in state.perf_stats.items():
                    cycle_counts[idx] = stats.latency
                rendered = build_gutter(asm_lines, cycle_counts)
                self.assembly_view.set_asm(rendered)
            else:
                from rich.text import Text
                self.assembly_view.set_asm(Text(state.asm_content or "(no assembly)"))

        except Exception:
            # Fallback: just show raw asm text
            from rich.text import Text
            self.assembly_view.set_asm(
                Text(state.asm_content or "(no assembly)")
            )

        # Update status bar
        if state.compiler_output and "error" in state.compiler_output.lower():
            self.status_bar.set_status(status="error", errors=1)
            self.notify("Compilation error", severity="error")
        elif state.compiler_output and "warning" in state.compiler_output.lower():
            self.status_bar.set_status(status="ready", errors=0)
            self.notify("Recompiled with warnings", severity="warning")
        else:
            self.status_bar.set_status(status="ready", errors=0)
            self.notify("Updated")

    # -- actions --------------------------------------------------

    def action_refresh(self) -> None:
        """Keybinding 'r' -> manual recompile."""
        if self.engine is not None:
            self.status_bar.set_status(status="compiling…")
            self.engine.refresh()
        else:
            self._show_error("Engine not initialized")

    # -- helpers ---------------------------------------------------

    def _show_error(self, text: str) -> None:
        self.status_bar.set_status(status="error", errors=1)
        from rich.text import Text
        self.assembly_view.set_asm(Text(text, style="bold red"))


def run_tui(source_file: str):
    """Entry point called by main.py — matches main branch interface."""
    app = LocalBoltApp(source_file)
    app.run()
