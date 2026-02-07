import json
import os
from pathlib import Path
from typing import Dict, Any

DEFAULT_CONFIG = {
    "compiler": "g++",
    "opt_level": "-O0",
    "flags": []
}

class ConfigManager:
    def __init__(self):
        self.config_dir = Path.home() / ".localbolt"
        self.config_file = self.config_dir / "config.json"
        self.config = self.load_config()

    def load_config(self) -> Dict[str, Any]:
        if not self.config_dir.exists():
            self.config_dir.mkdir(parents=True)
        
        config = DEFAULT_CONFIG.copy()
        if self.config_file.exists():
            try:
                with open(self.config_file, "r") as f:
                    user_cfg = json.load(f)
                    config.update(user_cfg)
            except:
                pass
        return config

    def save_config(self):
        with open(self.config_file, "w") as f:
            json.dump(self.config, f, indent=4)

    def get(self, key: str, default: Any = None) -> Any:
        return self.config.get(key, default)

    def set(self, key: str, value: Any):
        self.config[key] = value
        self.save_config()
