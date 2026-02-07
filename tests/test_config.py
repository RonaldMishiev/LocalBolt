import sys
import os

# Add src to python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from localbolt.compiler import CompilerDriver
from localbolt.utils.config import ConfigManager

def test_compiler_switching():
    print("--- Testing Compiler Discovery ---")
    available = CompilerDriver.discover_compilers()
    print(f"Found on system: {available}")
    
    driver = CompilerDriver()
    
    for c in available:
        print(f"Switching to: {c}")
        driver.set_compiler(c)
        assert driver.compiler == c
        
    print("Compiler switching works!")

def test_config_persistence():
    print("\n--- Testing Config Persistence ---")
    mgr = ConfigManager()
    original_compiler = mgr.get("compiler")
    
    test_val = "clang++" if original_compiler != "clang++" else "g++"
    print(f"Setting compiler to {test_val} in config...")
    mgr.set("compiler", test_val)
    
    # Reload
    new_mgr = ConfigManager()
    assert new_mgr.get("compiler") == test_val
    print("Config persistence works!")
    
    # Cleanup
    mgr.set("compiler", original_compiler)

if __name__ == "__main__":
    test_compiler_switching()
    test_config_persistence()
