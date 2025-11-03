"""
Configuration Manager

Handles loading, saving, and validation of simulation configuration.
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional
from copy import deepcopy


class ConfigManager:
    """
    Manages configuration for FODEMIR-Sim application.
    
    Handles loading default configurations, user configurations,
    validation, and saving modified configurations.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize configuration manager.
        
        Args:
            config_path: Path to user configuration file. If None, uses default config.
        """
        self.config_dir = Path(__file__).parent
        self.default_config_path = self.config_dir / "default_config.json"
        self.user_config_path = Path(config_path) if config_path else None
        
        # Load default configuration
        self.config = self.load_default_config()
        
        # Override with user configuration if provided
        if self.user_config_path and self.user_config_path.exists():
            self.load_user_config(self.user_config_path)
    
    def load_default_config(self) -> Dict[str, Any]:
        """
        Load default configuration from JSON file.
        
        Returns:
            Dictionary containing default configuration
        """
        try:
            with open(self.default_config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            return config
        except Exception as e:
            raise RuntimeError(f"Failed to load default configuration: {e}")
    
    def load_user_config(self, config_path: Path) -> None:
        """
        Load user configuration and merge with default config.
        
        Args:
            config_path: Path to user configuration file
        """
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                user_config = json.load(f)
            
            # Deep merge user config into default config
            self.config = self._deep_merge(self.config, user_config)
        except Exception as e:
            print(f"Warning: Failed to load user configuration: {e}")
            print("Using default configuration.")
    
    def save_config(self, save_path: Optional[Path] = None) -> None:
        """
        Save current configuration to file.
        
        Args:
            save_path: Path to save configuration. If None, uses user_config_path.
        """
        if save_path is None:
            save_path = self.user_config_path
        
        if save_path is None:
            raise ValueError("No save path specified and no user config path set.")
        
        save_path = Path(save_path)
        save_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            with open(save_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            raise RuntimeError(f"Failed to save configuration: {e}")
    
    def get(self, key_path: str, default: Any = None) -> Any:
        """
        Get configuration value using dot notation.
        
        Args:
            key_path: Dot-separated path to configuration key (e.g., 'forest_generation.area_m2')
            default: Default value if key not found
        
        Returns:
            Configuration value or default
        """
        keys = key_path.split('.')
        value = self.config
        
        try:
            for key in keys:
                value = value[key]
            return value
        except (KeyError, TypeError):
            return default
    
    def set(self, key_path: str, value: Any) -> None:
        """
        Set configuration value using dot notation.
        
        Args:
            key_path: Dot-separated path to configuration key
            value: Value to set
        """
        keys = key_path.split('.')
        config = self.config
        
        # Navigate to the parent of the target key
        for key in keys[:-1]:
            if key not in config:
                config[key] = {}
            config = config[key]
        
        # Set the final key
        config[keys[-1]] = value
    
    def validate(self) -> bool:
        """
        Validate configuration values.
        
        Returns:
            True if configuration is valid, raises ValueError otherwise
        """
        # Validate forest generation parameters
        forest_config = self.config.get('forest_generation', {})
        if forest_config.get('area_m2', 0) <= 0:
            raise ValueError("Forest area must be positive")
        if forest_config.get('tree_density_per_ha', 0) <= 0:
            raise ValueError("Tree density must be positive")
        
        # Validate EM propagation parameters
        em_config = self.config.get('em_propagation', {})
        if em_config.get('frequency_mhz', 0) <= 0:
            raise ValueError("Frequency must be positive")
        if em_config.get('tx_power_dbm', -1000) < -100 or em_config.get('tx_power_dbm', 1000) > 100:
            raise ValueError("TX power must be reasonable (-100 to 100 dBm)")
        
        # Validate optimization parameters
        opt_config = self.config.get('optimization', {})
        algo = opt_config.get('algorithm', 'nsga2')
        if algo not in ['nsga2', 'smpso']:
            raise ValueError(f"Unknown optimization algorithm: {algo}")
        
        # Validate UAV parameters
        uav_config = self.config.get('uav_planning', {})
        if uav_config.get('uav_speed_m_per_s', 0) <= 0:
            raise ValueError("UAV speed must be positive")
        if uav_config.get('battery_capacity_wh', 0) <= 0:
            raise ValueError("Battery capacity must be positive")
        
        return True
    
    def reset_to_default(self) -> None:
        """Reset configuration to default values."""
        self.config = self.load_default_config()
    
    def get_section(self, section: str) -> Dict[str, Any]:
        """
        Get entire configuration section.
        
        Args:
            section: Section name (e.g., 'forest_generation')
        
        Returns:
            Dictionary containing section configuration
        """
        return deepcopy(self.config.get(section, {}))
    
    def update_section(self, section: str, values: Dict[str, Any]) -> None:
        """
        Update entire configuration section.
        
        Args:
            section: Section name
            values: Dictionary of values to update
        """
        if section not in self.config:
            self.config[section] = {}
        
        self.config[section].update(values)
    
    @staticmethod
    def _deep_merge(base: Dict, override: Dict) -> Dict:
        """
        Deep merge two dictionaries.
        
        Args:
            base: Base dictionary
            override: Dictionary with override values
        
        Returns:
            Merged dictionary
        """
        result = deepcopy(base)
        
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = ConfigManager._deep_merge(result[key], value)
            else:
                result[key] = deepcopy(value)
        
        return result
    
    def __repr__(self) -> str:
        return f"ConfigManager(config_keys={list(self.config.keys())})"


# Convenience function for quick config loading
def load_config(config_path: Optional[str] = None) -> ConfigManager:
    """
    Load configuration.
    
    Args:
        config_path: Optional path to user configuration file
    
    Returns:
        ConfigManager instance
    """
    return ConfigManager(config_path)


