import yaml
import os
from typing import Dict, Any
from pathlib import Path

class ConfigManager:
    """Manages hierarchical configuration with inheritance"""
    
    def __init__(self, config_path: str):
        self.config_dir = Path(config_path).parent
        self.config = self._load_config(config_path)
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load config with parent inheritance"""
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        # Handle parent config
        if 'parent' in config:
            parent_path = self.config_dir / config['parent']
            parent_config = self._load_config(parent_path)
            # Deep merge parent and child configs
            config = self._deep_merge(parent_config, config)
            del config['parent']
        
        return config
    
    def _deep_merge(self, parent: Dict, child: Dict) -> Dict:
        """Deep merge two dictionaries"""
        result = parent.copy()
        
        for key, value in child.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value
        
        return result
    
    def get(self, key: str, default=None):
        """Get config value with dot notation support"""
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default
        
        return value if value is not None else default
        