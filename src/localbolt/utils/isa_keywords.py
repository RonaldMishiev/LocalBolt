"""
ISA-specific keyword patterns for assembly syntax highlighting.
Each major ISA (x86, ARM) has its own REGISTERS, SIZE_KEYWORDS, and INSTRUCTIONS.
NUMBERS is shared across ISAs.
"""
import re
import platform

# ---------------------------------------------------------------------------
# Shared: number literals (hex, binary, decimal)
# ---------------------------------------------------------------------------
NUMBERS = re.compile(r"\b(0x[0-9a-fA-F]+|0b[01]+|[0-9]+)\b")

# ---------------------------------------------------------------------------
# x86 (x86_64, AMD64, i386)
# ---------------------------------------------------------------------------
_X86_REGISTERS = re.compile(
    r"\b("
    r"r[abcd]x|r[sd]i|r[bs]p|r(?:8|9|1[0-5])[dwb]?"
    r"|e[abcd]x|e[sd]i|e[bs]p"
    r"|[abcd][hl]|[abcd]x|[sd]il?|[bs]pl?"
    r"|xmm[0-9]+|ymm[0-9]+|zmm[0-9]+"
    r")\b",
    re.IGNORECASE,
)

_X86_SIZE_KEYWORDS = re.compile(r"\b(DWORD|QWORD|WORD|BYTE|PTR)\b")

_X86_INSTRUCTIONS = re.compile(
    r"\b("
    r"movs?[xzbw]?|lea|add|subs?|imul|idiv|mul|div|sdiv|inc|dec"
    r"|cmp|test|and|or|xor|not|shl|shr|sar|sal"
    r"|jmp|je|jne|jz|jnz|jg|jge|jl|jle|ja|jae|jb|jbe"
    r"|call|ret|push|pop|nop|int|syscall|leave|enter"
    r"|cmov\w+"
    r")\b",
    re.IGNORECASE,
)

# ---------------------------------------------------------------------------
# ARM (ARM64 / AArch64)
# ---------------------------------------------------------------------------
_ARM_REGISTERS = re.compile(
    r"\b("
    r"[wx][0-9]{1,2}|sp|fp|lr"
    r")\b",
    re.IGNORECASE,
)

# ARM assembly typically doesn't use DWORD/QWORD/etc.; omit or minimal.
_ARM_SIZE_KEYWORDS = re.compile(r"\b(PTR)\b")

_ARM_INSTRUCTIONS = re.compile(
    r"\b("
    r"movs?[xzbw]?|add|subs?|imul|idiv|mul|div|sdiv|inc|dec"
    r"|cmp|test|and|or|xor|not|shl|shr|sar|sal"
    r"|call|ret|nop"
    r"|adrp|bl|b\.|cbnz"
    r")\b",
    re.IGNORECASE,
)

# ---------------------------------------------------------------------------
# ISA detection and keyword lookup
# ---------------------------------------------------------------------------
def get_isa() -> str:
    """Return 'x86' or 'arm' based on platform.machine()."""
    machine = platform.machine().lower()
    if machine in ("x86_64", "amd64", "i386", "i686", "x86"):
        return "x86"
    if machine in ("arm64", "aarch64", "aarch64_be", "armv8", "arm64e"):
        return "arm"
    # Default to x86 for unknown (e.g. emulated or future)
    return "x86"


def get_keywords(isa: str | None = None) -> dict:
    """
    Return keyword dict for the given ISA: REGISTERS, SIZE_KEYWORDS, INSTRUCTIONS.
    NUMBERS is shared; callers can use isa_keywords.NUMBERS.
    If isa is None, uses get_isa().
    """
    if isa is None:
        isa = get_isa()
    if isa == "x86":
        return {
            "REGISTERS": _X86_REGISTERS,
            "SIZE_KEYWORDS": _X86_SIZE_KEYWORDS,
            "INSTRUCTIONS": _X86_INSTRUCTIONS,
        }
    if isa == "arm":
        return {
            "REGISTERS": _ARM_REGISTERS,
            "SIZE_KEYWORDS": _ARM_SIZE_KEYWORDS,
            "INSTRUCTIONS": _ARM_INSTRUCTIONS,
        }
    # fallback to x86
    return get_keywords("x86")
