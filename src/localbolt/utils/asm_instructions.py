"""
ISA-specific assembly instruction help text.
Each entry: (Description, Example, Meaning).
Use get_asm_instructions(isa) to get the dict for the current or given ISA.
"""
from .isa_keywords import get_isa

# ---------------------------------------------------------------------------
# x86 (x86_64 / Intel syntax)
# ---------------------------------------------------------------------------
ASM_INSTRUCTIONS_X86 = {
    "MOV": ("Copies data from one location to another.", "mov eax, ebx", "Copy value from EBX into EAX"),
    "PUSH": ("Pushes a value onto the stack.", "push rax", "Put RAX onto the stack"),
    "POP": ("Pops a value from the stack into a register.", "pop rdi", "Take value from top of stack into RDI"),
    "ADD": ("Adds two operands and stores the result in the first.", "add eax, ebx", "EAX = EAX + EBX"),
    "SUB": ("Subtracts second operand from the first.", "sub eax, 1", "EAX = EAX - 1"),
    "IMUL": ("Signed multiplication.", "imul rax, rbx", "RAX = RAX * RBX"),
    "CMP": ("Compares two operands by setting CPU flags.", "cmp eax, 0", "Check if EAX is zero"),
    "RET": ("Returns from a function.", "ret", "Return to the calling function"),
    "LEA": ("Load Effective Address (calculates pointer).", "lea rax, [rbp-8]", "Get the address of a local variable"),
    "CDQ": ("Sign-extends EAX into EDX:EAX. Prepared for 64-bit division.", "cdq", "Sign-extend EAX into EDX"),
    "IDIV": ("Signed divide. Divides EDX:EAX by the operand.", "idiv ecx", "EAX = Quotient, EDX = Remainder"),
    "INC": ("Increments an operand by 1.", "inc eax", "EAX = EAX + 1"),
    "DEC": ("Decrements an operand by 1.", "dec ebx", "EBX = EBX - 1"),
    "JMP": ("Unconditional jump to a label or address.", "jmp .L2", "Always jump to label .L2"),
    "XOR": ("Bitwise exclusive OR. Often used to zero a register.", "xor eax, eax", "Set EAX to 0"),
    "AND": ("Bitwise AND.", "and eax, 7", "Keep only the lower 3 bits of EAX"),
    "OR": ("Bitwise OR.", "or ebx, 1", "Set the lowest bit of EBX to 1"),
    "NOP": ("No Operation. Does nothing for one cycle.", "nop", "Wait/Do nothing"),
    "CALL": ("Calls a function; pushes return address to stack.", "call printf", "Execute the printf function"),
    "TEST": ("Logical compare using AND (sets flags, no result saved).", "test eax, eax", "Check if EAX is zero or negative"),
    "MOVZX": ("Move with Zero-Extend (copies smaller to larger).", "movzx rax, byte ptr [rbp-1]", "Copy byte to 64-bit reg, zero the rest"),
    "SHL": ("Shift Left: Multiplies by powers of 2.", "shl eax, 1", "EAX = EAX * 2"),
    "SAL": ("Shift Arithmetic Left (same as SHL).", "sal eax, 1", "EAX = EAX * 2"),
    "SHR": ("Shift Right (logical): Divides by powers of 2.", "shr ebx, 2", "EBX = EBX / 4"),
    "SAR": ("Shift Right (arithmetic): Preserves sign.", "sar eax, 1", "Signed EAX / 2"),
    "LEAVE": ("High-level Procedure Exit (restores EBP and ESP).", "leave", "Clean up stack frame"),
    "SYSCALL": ("System Call: Transitions to kernel mode.", "syscall", "Request OS service"),
    "JE": ("Jump if Equal.", "je .Lerror", "Jump if result was zero"),
    "JZ": ("Jump if Zero.", "jz .Lerror", "Jump if zero flag set"),
    "JNE": ("Jump if Not Equal.", "jne .Lloop", "Jump if result was not zero"),
    "JNZ": ("Jump if Not Zero.", "jnz .Lloop", "Jump if not zero"),
    "JG": ("Jump if Greater (signed).", "jg .Lbigger", "Jump if left > right"),
    "JL": ("Jump if Less (signed).", "jl .Lsmaller", "Jump if left < right"),
    "JGE": ("Jump if Greater or Equal (signed).", "jge .Ltop", "Jump if left >= right"),
    "MUL": ("Unsigned integer multiplication.", "mul ecx", "EDX:EAX = EAX * ECX (unsigned)"),
}

# ---------------------------------------------------------------------------
# ARM (ARM64 / AArch64)
# ---------------------------------------------------------------------------
ASM_INSTRUCTIONS_ARM = {
    "MOV": ("Copies data from one location to another.", "mov x0, x1", "Copy value from X1 into X0"),
    "ADD": ("Adds two operands and stores the result in the first.", "add x0, x1, x2", "x0 = x1 + x2"),
    "SUB": ("Subtracts second from first.", "sub x0, x1, x2", "x0 = x1 - x2"),
    "SUBS": ("Subtracts and updates flags (for conditional branches).", "subs x0, x1, x2", "x0 = x1 - x2; flags updated"),
    "MUL": ("Multiply.", "mul x0, x1, x2", "x0 = x1 * x2"),
    "SDIV": ("Signed integer division.", "sdiv x0, x1, x2", "x0 = x1 / x2 (signed)"),
    "CMP": ("Compares two operands by setting flags.", "cmp w0, #0", "Check if W0 is zero"),
    "RET": ("Returns from a function.", "ret", "Return to the calling function"),
    "INC": ("Increments (ARM: use ADD reg, reg, #1).", "add w0, w0, #1", "W0 = W0 + 1"),
    "DEC": ("Decrements (ARM: use SUB reg, reg, #1).", "sub w0, w0, #1", "W0 = W0 - 1"),
    "XOR": ("Bitwise exclusive OR.", "eor x0, x0, x0", "Zero X0"),
    "AND": ("Bitwise AND.", "and x0, x0, #7", "Keep lower 3 bits of X0"),
    "OR": ("Bitwise OR.", "orr x0, x0, #1", "Set lowest bit of X0"),
    "NOP": ("No Operation.", "nop", "Do nothing for one cycle"),
    "CALL": ("Calls a function (ARM: use BL).", "bl _printf", "Execute the printf function"),
    "TEST": ("Logical compare (ARM: use CMP or TST).", "tst w0, w0", "Check if W0 is zero"),
    "SHL": ("Shift Left.", "lsl x0, x1, #2", "x0 = x1 << 2"),
    "SHR": ("Shift Right (logical).", "lsr x0, x1, #2", "x0 = x1 >> 2 (unsigned)"),
    "SAR": ("Shift Right (arithmetic).", "asr x0, x1, #1", "x0 = x1 >> 1 (signed)"),
    "LDR": ("Load Register: Loads a value from memory.", "ldr x0, [x1]", "Load value at address x1 into x0"),
    "STR": ("Store Register: Stores a register into memory.", "str x0, [sp, #8]", "Store x0 at stack offset 8"),
    "LDP": ("Load Pair: Loads two registers from consecutive memory.", "ldp x29, x30, [sp], #16", "Restore FP and LR"),
    "STP": ("Store Pair: Stores two registers into consecutive memory.", "stp x29, x30, [sp, #-16]!", "Save FP and LR"),
    "ADRP": ("Address Page: Form PC-relative address to a 4KB page.", "adrp x0, label@PAGE", "Base address of a global"),
    "BL": ("Branch with Link: Calls a function.", "bl _printf", "Execute the printf function"),
    "B": ("Branch: Unconditional jump.", "b .L2", "Always jump to label .L2"),
    "B.": ("Conditional Branch (e.g., B.EQ, B.NE).", "b.eq .Lerror", "Jump if previous comparison was equal"),
    "CBNZ": ("Compare and Branch if Not Zero.", "cbnz x0, .Lloop", "If x0 != 0, branch to .Lloop"),
    "STUR": ("Store Unscaled: Store with unscaled offset.", "stur w0, [x29, #-4]", "Store local variable on stack"),
    "LDUR": ("Load Unscaled: Load with unscaled offset.", "ldur w0, [x29, #-4]", "Load local variable from stack"),
}


def get_asm_instructions(isa: str | None = None) -> dict:
    """
    Return the instruction-help dict for the given ISA.
    Each value is (description, example, meaning).
    If isa is None, uses get_isa() (platform.machine()).
    """
    if isa is None:
        isa = get_isa()
    if isa == "x86":
        return ASM_INSTRUCTIONS_X86.copy()
    if isa == "arm":
        return ASM_INSTRUCTIONS_ARM.copy()
    return ASM_INSTRUCTIONS_X86.copy()
