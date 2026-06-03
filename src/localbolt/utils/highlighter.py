import re
import shutil
from pathlib import Path
from rich.text import Text

from .isa_keywords import get_isa, get_keywords, NUMBERS

# Palette provided by user
C_FOREGROUND = "#EBEEEE"
C_TEXT = "#191A1A"
C_MISC1 = "#9FBFC5" # Muted Blue-Grey
C_MISC2 = "#007b9a" # Strong Cyan (Instructions)
C_MISC3 = "#00796b" # Strong Teal (Labels)
C_MISC4 = "#af5f00" # Strong Orange (Registers)

_ERR_FILE = Path(__file__).resolve().parents[3] / "highlight_errors.txt"

# ISA-specific keyword regexes (resolved once at import from isa_keywords)
_ISA = get_isa()
_KEYWORDS = get_keywords(_ISA)
REGISTERS = _KEYWORDS["REGISTERS"]
SIZE_KEYWORDS = _KEYWORDS["SIZE_KEYWORDS"]
INSTRUCTIONS = _KEYWORDS["INSTRUCTIONS"]

def _severity_styles(cycles: int | None) -> tuple[str, str]:
    """Light-mode compatible heatmap palette."""
    if cycles is None: return (C_TEXT, f"on {C_FOREGROUND}")
    # Low: Pale green
    if cycles <= 1: return (C_TEXT, "on #d1e7dd")
    # Med: Pale amber
    if cycles <= 4: return (C_TEXT, "on #fff3cd")
    # High: Pale red
    return (C_TEXT, "on #f8d7da")

def _highlight_asm_line(line: str, bg: str) -> Text:
    # Debug: log the raw (already demangled) line we are asked to render.
    # NOTE: This is called frequently during rendering and can grow highlight_errors.txt quickly.
    try:
        with _ERR_FILE.open("a", encoding="utf-8") as f:
            f.write(line.rstrip("\n") + "\n")
    except Exception:
        with _ERR_FILE.open("a", encoding="utf-8") as f:
            f.write("Error in highlight_asm_line to highlight_errors.txt\n")

    segment = Text()
    stripped = line.lstrip()
    if stripped.startswith("#") or stripped.startswith(";"):
        segment.append(line, style=f"italic #888888 {bg}")
        return segment

    token_styles: list[str | None] = [None] * len(line)

    # Apply Palette
    # Labels / function headers (e.g. "binexp(int, int):" or "_Z6binexpii:")
    # Treat everything from start of line up to the first ':' as the label token.
    # Do not treat lines containing "::" as labels (e.g. C++ symbols like std::cout).
    # label_match = re.match(r"^(\s*\.?\w+\s*:)", line)
    label_match = re.match(r"^(?!.*::)(\s*[^:\s][^:]*:\s*)", line)
    if label_match:
        for j in range(label_match.start(), label_match.end()):
            token_styles[j] = f"bold {C_MISC3}" # Teal Labels

    # Only the first instruction match on the line gets instruction (blue) highlighting
    instruction_span = None  # (start, end) of the highlighted instruction
    for m in INSTRUCTIONS.finditer(line):
        if instruction_span is None:
            for j in range(m.start(), m.end()):
                # Don't override existing styling (e.g. labels / function headers)
                if token_styles[j] is None:
                    token_styles[j] = f"bold {C_MISC2}"  # Cyan Instructions
            instruction_span = (m.start(), m.end())
        # further instruction matches on the same line are left unstyled

    for m in SIZE_KEYWORDS.finditer(line):
        for j in range(m.start(), m.end()):
            token_styles[j] = "#a37acc" # Muted Purple

    for m in NUMBERS.finditer(line):
        for j in range(m.start(), m.end()):
            token_styles[j] = "#666666"

    # Highlight registers. If a register match also matches an instruction,
    # only style it as a register if a DIFFERENT instruction was already
    # highlighted on this line (so e.g. "bl" on a "bl ..." line stays blue,
    # but "sp" on any instruction line is orange).
    for m in REGISTERS.finditer(line):
        also_instruction = INSTRUCTIONS.fullmatch(line[m.start():m.end()])
        if also_instruction:
            # This token is both a register and an instruction —
            # only colour it as a register if a different instruction is on the line
            if instruction_span is None:
                continue  # no instruction on the line, leave unstyled
            if m.start() == instruction_span[0] and m.end() == instruction_span[1]:
                continue  # same span as the highlighted instruction, keep it blue
        for j in range(m.start(), m.end()):
            token_styles[j] = f"bold {C_MISC4}" # Orange Registers

    i = 0
    while i < len(line):
        cur_style = token_styles[i]
        j = i
        while j < len(line) and token_styles[j] == cur_style:
            j += 1
        full_style = f"{cur_style} {bg}" if cur_style else f"{C_TEXT} {bg}"
        segment.append(line[i:j], style=full_style.strip())
        i = j
    return segment


# Public aliases for asm_app.py and other consumers
highlight_asm_line = _highlight_asm_line
severity_styles = _severity_styles


def build_gutter(asm_lines: list[str], cycle_counts: dict[int, int], width: int = 150) -> Text:
    gutter_width = 6
    result = Text(no_wrap=True)
    for i, line in enumerate(asm_lines):
        line_num = i + 1
        cycles = cycle_counts.get(line_num)
        fg_style, bg = _severity_styles(cycles)
        result.append_text(_highlight_asm_line(line, bg))
        padding_needed = max(1, width - len(line) - gutter_width)
        result.append(" " * padding_needed, style=bg.strip() or None)
        if cycles is not None:
            result.append(f"{cycles:>{gutter_width}}c", style=f"bold {C_TEXT} {bg}".strip())
        else:
            result.append(" " * (gutter_width + 1), style=bg.strip() or None)
        if line_num < len(asm_lines):
            result.append("\n")
    return result