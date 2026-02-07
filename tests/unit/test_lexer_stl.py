import sys
import os
import unittest

# Add src to python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))

from localbolt.parsing.lexer import clean_assembly_with_mapping

class TestSTLCleaning(unittest.TestCase):
    def test_filter_includes(self):
        """
        Verify that instructions from file ID 2 (iostream) are filtered out,
        while instructions from file ID 1 (main.cpp) are kept.
        """
        # Mock Assembly with two files
        # File 1: main.cpp (The user code)
        # File 2: /usr/include/iostream (The STL noise)
        raw_asm = """
            .file 1 "main.cpp"
            .file 2 "/usr/include/iostream"
            
            .text
            .globl main
            .type main, @function
        main:
        .LFB0:
            .loc 1 10 0
            pushq %rbp
            movq %rsp, %rbp
            
            .loc 2 500 0   # Switch to iostream
            movl $0, %eax  # This is STL noise
            popq %rbp
            
            .loc 1 12 0    # Back to main.cpp
            ret
        """
        
        # We tell the lexer that "main.cpp" is our source file
        cleaned, mapping = clean_assembly_with_mapping(raw_asm, source_filename="main.cpp")
        
        lines = cleaned.splitlines()
        print(f"Cleaned lines: {lines}")
        
        # Assertions
        self.assertIn("pushq %rbp", cleaned, "User code should be present")
        self.assertIn("movq %rsp, %rbp", cleaned, "User code should be present")
        self.assertNotIn("movl $0, %eax", cleaned, "STL code should be filtered out")
        self.assertIn("ret", cleaned, "User return should be present")
        
        # Check mapping logic
        # The 'pushq' (index 1 probably) should map to line 10
        # The 'ret' should map to line 12
        # The 'movl' should NOT exist in the mapping
        
        # Note: Indexing depends on exactly how many lines are kept.
        # Let's check the values exist in the map values
        self.assertIn(10, mapping.values())
        self.assertIn(12, mapping.values())
        self.assertNotIn(500, mapping.values())

if __name__ == "__main__":
    unittest.main()
