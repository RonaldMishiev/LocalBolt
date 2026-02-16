import sys
import os

# Add src to python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'src')))

from localbolt.utils.asm_instructions import get_asm_instructions, ASM_INSTRUCTIONS_X86, ASM_INSTRUCTIONS_ARM
from localbolt.utils.asm_help import create_gradient_header
from rich.text import Text

def test_asm_instructions_content():
    """Verify that ISA-specific instruction dicts are populated and have correct structure."""
    x86 = get_asm_instructions("x86")
    arm = get_asm_instructions("arm")
    assert len(x86) >= 20
    assert len(arm) >= 20
    assert "MOV" in x86
    assert "PUSH" in x86
    assert "LEA" in x86
    assert "MOV" in arm
    assert "BL" in arm
    assert "LDR" in arm
    assert "PUSH" not in arm

    # Check structure: (Description, Example, Meaning)
    for isa_name, d in [("x86", x86), ("arm", arm)]:
        data = d["MOV"]
        assert len(data) == 3, isa_name
        assert isinstance(data[0], str)
        assert isinstance(data[1], str)
        assert isinstance(data[2], str)
        assert "mov" in data[1].lower()

def test_gradient_header_generation():
    """Verify that the gradient header is generated as a Rich Text object."""
    title = "TEST HEADER"
    result = create_gradient_header(title)
    
    assert isinstance(result, Text)
    assert title in result.plain
    
    # Check that styles (colors) were applied
    assert len(result._spans) > 0

def test_instruction_sorting():
    """Ensure we can sort the instructions for display."""
    x86 = get_asm_instructions("x86")
    keys = list(x86.keys())
    sorted_keys = sorted(keys)
    assert len(sorted_keys) == len(keys)
    assert sorted_keys == sorted(keys)
    assert "ADD" in sorted_keys
    assert "MOV" in sorted_keys

if __name__ == "__main__":
    try:
        test_asm_instructions_content()
        print("test_asm_instructions_content PASSED")
        test_gradient_header_generation()
        print("test_gradient_header_generation PASSED")
        test_instruction_sorting()
        print("test_instruction_sorting PASSED")
        print("ALL ASM HELP UNIT TESTS PASSED!")
    except AssertionError as e:
        print(f"TEST FAILED: {e}")
        sys.exit(1)