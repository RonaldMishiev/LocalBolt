from dataclasses import dataclass
from typing import Optional

@dataclass
class CompilationResult:
    assembly: str          # The raw assembly code (for Member B to clean)
    error_msg: str         # Compiler stderr (if any)
    perf_report: str       # llvm-mca output
    cycle_count: int       # A parsed integer summary (e.g., 145 cycles)
    success: bool          # Did it compile?