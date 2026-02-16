from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.style import Style

from .asm_instructions import get_asm_instructions

# Theme Colors (Mosaic)
C_BG = "#EBEEEE"
C_TEXT = "#191A1A"
C_ACCENT1 = "#45d3ee" # Cyan
C_ACCENT2 = "#9FBFC5" # Muted Blue
C_ACCENT3 = "#94bfc1" # Teal
C_ACCENT4 = "#fecd91" # Orange

def create_gradient_header(title: str) -> Text:
    text = Text(f" {title} ", style="bold italic")
    # Gradient between Cyan and Blue-Grey
    start_rgb = (69, 211, 238) # #45d3ee
    end_rgb = (159, 191, 197)   # #9FBFC5
    
    for i in range(len(text)):
        ratio = i / len(text)
        r = int(start_rgb[0] + (end_rgb[0] - start_rgb[0]) * ratio)
        g = int(start_rgb[1] + (end_rgb[1] - start_rgb[1]) * ratio)
        b = int(start_rgb[2] + (end_rgb[2] - start_rgb[2]) * ratio)
        color = f"#{r:02x}{g:02x}{b:02x}"
        text.stylize(color, i, i+1)
    return text

def display_asm_help():
    # Force a light background for the whole console output if possible
    # Note: Rich doesn't easily set global terminal BG, so we wrap in a Panel
    console = Console()
    
    header = create_gradient_header("LOCALBOLT ASSEMBLY REFERENCE")
    
    table = Table(
        title="Popular Assembly Instructions", 
        title_style=f"bold {C_ACCENT3}",
        header_style=f"bold {C_ACCENT1}",
        box=None, # Clean look
        row_styles=["", f"on #f5f7f7"], # Subtle zebra striping on light bg
        expand=True
    )
    
    table.add_column("Instruction", style=f"bold {C_ACCENT1}", no_wrap=True)
    table.add_column("Description", style=C_TEXT)
    table.add_column("Example", style=f"bold {C_ACCENT4}")
    table.add_column("Meaning", style=C_ACCENT3)

    instructions = get_asm_instructions()
    for instr, (desc, example, meaning) in sorted(instructions.items()):
        table.add_row(instr, desc, example, meaning)

    # Wrap everything in a Panel with the light background
    main_panel = Panel(
        table,
        title=header,
        title_align="left",
        border_style=C_ACCENT2,
        padding=(1, 2),
        style=f"{C_TEXT} on {C_BG}"
    )

    console.print("\n")
    console.print(main_panel)
    console.print(f"\n[bold {C_TEXT}] Press Q or Ctrl+C to return to terminal.[/bold {C_TEXT}]")
