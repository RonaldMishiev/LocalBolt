from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Static, TextArea
from textual.containers import Horizontal, Vertical
from textual.binding import Binding
from textual.message import Message
from ..engine import BoltEngine
from ..utils.state import LocalBoltState

class LocalBoltApp(App):
    """The main LocalBolt TUI."""

    CSS = """
    Screen {
        background: #1e1e1e;
    }
    #left-pane {
        width: 50%;
        border-right: heavy $primary;
    }
    #right-pane {
        width: 50%;
    }
    .panel-title {
        background: $primary;
        color: white;
        text-align: center;
        width: 100%;
        padding: 0 1;
    }
    TextArea {
        border: none;
    }
    """

    BINDINGS = [
        Binding("q", "quit", "Quit", show=True),
        Binding("r", "refresh", "Manual Refresh", show=True),
    ]

    class StateUpdated(Message):
        """Internal message to trigger a UI update from any thread."""
        def __init__(self, state: LocalBoltState) -> None:
            super().__init__()
            self.state = state

    def __init__(self, source_file: str):
        super().__init__()
        self.engine = BoltEngine(source_file)
        # The engine will call this function whenever data changes
        self.engine.on_update_callback = lambda state: self.post_message(self.StateUpdated(state))

    def compose(self) -> ComposeResult:
        yield Header()
        yield Horizontal(
            Vertical(
                Static(" SOURCE ", classes="panel-title"),
                TextArea(id="source-view", language="cpp", read_only=True),
                id="left-pane"
            ),
            Vertical(
                Static(" ASSEMBLY ", classes="panel-title"),
                TextArea(id="asm-view", language="asm", read_only=True),
                id="right-pane"
            )
        )
        yield Footer()

    def on_mount(self) -> None:
        """Initialize the engine once the UI is ready."""
        self.engine.start()
        self.notify(f"Watching {self.engine.state.source_path}")

    def on_local_bolt_app_state_updated(self, message: StateUpdated) -> None:
        """Handles the StateUpdated message and refreshes widgets."""
        state = message.state
        source_view = self.query_one("#source-view", TextArea)
        asm_view = self.query_one("#asm-view", TextArea)
        
        # update the content
        source_view.text = state.source_code
        asm_view.text = state.asm_content
        
        if state.compiler_output and "warning" in state.compiler_output.lower():
            self.notify("Recompiled with warnings", severity="warning")
        elif state.compiler_output:
             self.notify("Recompile failed", severity="error")
        else:
            self.notify("Recompile successful")

    def action_refresh(self) -> None:
        """Manual refresh trigger."""
        self.engine.refresh()

    def on_unmount(self) -> None:
        """Ensure the background observer is stopped."""
        self.engine.stop()

def run_tui(source_file: str):
    app = LocalBoltApp(source_file)
    app.run()
