import json
import os
import shlex
from pathlib import Path
from typing import List, Optional

def find_compile_commands(start_path: Path) -> Optional[Path]:
    """
    Recursively searches upwards for compile_commands.json.
    """
    current = start_path.resolve()
    # Check current and parents up to root
    for parent in [current] + list(current.parents):
        # Check common build subdirectories
        search_locs = [
            parent / "compile_commands.json",
            parent / "build" / "compile_commands.json",
            parent / "out" / "compile_commands.json",
            parent / "debug" / "compile_commands.json",
        ]
        for loc in search_locs:
            if loc.exists():
                return loc
    return None

def get_flags_from_db(source_file: str, db_path: Path) -> List[str]:
    """
    Extracts flags and converts relative include paths to absolute.
    """
    try:
        with open(db_path, 'r') as f:
            commands = json.load(f)
            
        abs_source = str(Path(source_file).resolve())
        
        for entry in commands:
            entry_dir = Path(entry.get('directory', '.'))
            entry_file = str(Path(entry_dir, entry['file']).resolve())
            
            if entry_file == abs_source:
                args = shlex.split(entry['command'])
                useful_flags = []
                
                for arg in args[1:]:
                    # Handle Include Paths
                    if arg.startswith("-I"):
                        inc_path = arg[2:]
                        # If relative, make it absolute based on the JSON's directory
                        if not os.path.isabs(inc_path):
                            abs_inc = str((entry_dir / inc_path).resolve())
                            useful_flags.append(f"-I{abs_inc}")
                        else:
                            useful_flags.append(arg)
                    
                    # Keep other important flags
                    elif arg.startswith(("-D", "-std", "-f", "-m")):
                        useful_flags.append(arg)
                        
                return useful_flags
                
    except Exception as e:
        print(f"Error parsing compile commands: {e}")
        
    return []
