"""
Source Peek Widget
==================
A floating popup that displays the C++ source line corresponding to
whichever assembly line is currently under the cursor.
"""

from __future__ import annotations

from typing import Dict, List, Optional

from rich.text import Text
from textual.widgets import Static

# User Palette
C_BG = "#EBEEEE"
C_TEXT = "#191A1A"
C_ACCENT1 = "#45d3ee" # Cyan
C_ACCENT2 = "#9FBFC5" # Muted Blue
C_ACCENT3 = "#94bfc1" # Teal
C_ACCENT4 = "#fecd91" # Orange

class SourcePeekPanel(Static):
    """
    Floating popup showing the C++ source line that maps to the current
    assembly region.
    """

    DEFAULT_CSS = f"""
    SourcePeekPanel {{
        layer: overlay;
        width: 60;
        height: auto;
        max-height: 10;
        background: {C_BG};
        border: solid {C_ACCENT3};
        padding: 0 1;
        display: none; /* Hidden by default */
        offset: 2 2;   /* Initial offset, will be managed by App if needed */
    }}
    """

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)
        self._source_lines: List[str] = []
        self._asm_mapping: Dict[int, int] = {}
        self._current_source_line: Optional[int] = None

    def update_context(
        self,
        source_lines: List[str],
        asm_mapping: Dict[int, int],
    ) -> None:
        self._source_lines = source_lines
        self._asm_mapping = asm_mapping

    def show_for_asm_line(self, asm_line: int) -> None:
        """
        Look up which C++ source line corresponds to the given assembly
        line index (0-based) and display it.
        """
        src_num = self._asm_mapping.get(asm_line)

        # Walk backwards to find the nearest mapped source line
        if src_num is None:
            for offset in range(1, 20):
                if asm_line - offset < 0: break
                src_num = self._asm_mapping.get(asm_line - offset)
                if src_num is not None:
                    break

        if src_num is None:
            self.display = False
            return

        self.display = True
        self._current_source_line = src_num
        self._render_line(src_num)

    def _render_line(self, line_num: int) -> None:
        """Render a single C++ source line with surrounding context."""
        if not self._source_lines or line_num < 1 or line_num > len(self._source_lines):
            self.display = False
            return

        code = self._source_lines[line_num - 1]
        text = Text()

        # Header
        text.append(" C++ SOURCE PEEK ", style=f"bold {C_ACCENT3} on {C_BG}")
        text.append("\n\n")

        # Previous Line
        if line_num >= 2:
            prev = self._source_lines[line_num - 2]
            text.append(f" {line_num - 1:>4} │ ", style=f"dim {C_TEXT}")
            text.append(prev, style=f"dim {C_TEXT}")
            text.append("\n")

        # Active Line (Highlighted)
        text.append(f"►{line_num:>4} │ ", style=f"bold {C_ACCENT4}")
        text.append(code, style=f"bold {C_TEXT} on {C_ACCENT2}")
        text.append("\n")

        # Next Line
        if line_num < len(self._source_lines):
            nxt = self._source_lines[line_num]
            text.append(f" {line_num + 1:>4} │ ", style=f"dim {C_TEXT}")
            text.append(nxt, style=f"dim {C_TEXT}")

        self.update(text)