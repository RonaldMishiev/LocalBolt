import re
from typing import Dict, List, NamedTuple

class InstructionStats(NamedTuple):
    latency: int
    uops: float
    throughput: float

def parse_mca_output(mca_text: str) -> Dict[int, InstructionStats]:
    """
    Parses the 'Instruction Info' section of llvm-mca output.
    Returns a mapping of instruction index to its performance stats.
    """
    stats_map = {}
    
    # We are looking for the table under "Instruction Info:"
    # It looks like: [index]: {latency, uops, throughput, ...}
    # Example: [0]: {1, 0.50, 0.50, 0.00,  - }     add	edi, esi
    
    in_info_section = False
    # Regex to capture: [index], latency, uops, throughput
    pattern = re.compile(r"^\s*\[(\d+)\]:\s*\{(\d+),\s*([\d\.]+),\s*([\d\.]+)")

    for line in mca_text.splitlines():
        if "Instruction Info:" in line:
            in_info_section = True
            continue
        
        if in_info_section:
            # If we hit an empty line or a new section header, we might be done
            if line.strip() == "" or (":" in line and "[" not in line):
                if stats_map: # If we already found stats, we are done with this section
                    in_info_section = False
                continue

            match = pattern.match(line)
            if match:
                idx = int(match.group(1))
                latency = int(match.group(2))
                uops = float(match.group(3))
                throughput = float(match.group(4))
                
                stats_map[idx] = InstructionStats(latency, uops, throughput)

    return stats_map
