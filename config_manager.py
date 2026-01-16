#!/usr/bin/env python3
"""
Configuration Manager Module
Handles application configuration and settings
"""

import json
from pathlib import Path
from typing import Any, Dict


class ConfigManager:
    """Manages application configuration"""

    DEFAULT_CONFIG = {
        'can_interface': 'can0',
        'can_bitrate': 500000,
        'dbc_file': 'DCDC_COMETI_Primary_Customer_001_3units.dbc',
        'log_directory': './logs',
        'auto_reconnect': True,
        'message_buffer_size': 1000,
        'refresh_rate_ms': 100,
        'theme': 'default',
        'units': {
            'voltage': 'V',
            'current': 'A',
            'power': 'W',
            'temperature': 'C'
        },
        'converters': {
            'DCDC_Primary': {
                'enabled': True,
                'alias': 'Converter 1',
                'color': '#FF6B6B'
            },
            'DCDC_Primary_1': {
                'enabled': True,
                'alias': 'Converter 2',
                'color': '#4ECDC4'
            },
            'DCDC_Primary_2': {
                'enabled': True,
                'alias': 'Converter 3',
                'color': '#95E1D3'
            }
        },
        'alarms': {
            'overvoltage_threshold': 850,
            'undervoltage_threshold': 150,
            'overcurrent_threshold': 150,
            'overtemperature_threshold': 85,
            'enable_sound': True
        }
    }

    def __init__(self, config_file: str = 'config.json'):
        self.config_file = Path(config_file)
        self.config: Dict[str, Any] = {}

        # Load configuration
        self.load()

    def load(self) -> None:
        """Load configuration from file"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    self.config = json.load(f)
                print(f"✓ Loaded configuration from: {self.config_file}")
            except Exception as e:
                print(f"⚠ Failed to load config: {e}")
                self.config = self.DEFAULT_CONFIG.copy()
        else:
            # Use default config
            self.config = self.DEFAULT_CONFIG.copy()
            self.save()

    def save(self) -> None:
        """Save configuration to file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
            print(f"✓ Saved configuration to: {self.config_file}")
        except Exception as e:
            print(f"⚠ Failed to save config: {e}")

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value

        Args:
            key: Configuration key (supports nested keys with dots, e.g., 'alarms.enable_sound')
            default: Default value if key not found

        Returns:
            Configuration value
        """
        # Support nested keys
        keys = key.split('.')
        value = self.config

        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default

        return value

    def set(self, key: str, value: Any) -> None:
        """
        Set configuration value

        Args:
            key: Configuration key (supports nested keys with dots)
            value: Value to set
        """
        # Support nested keys
        keys = key.split('.')

        if len(keys) == 1:
            self.config[key] = value
        else:
            # Navigate to nested dict
            current = self.config
            for k in keys[:-1]:
                if k not in current:
                    current[k] = {}
                current = current[k]

            current[keys[-1]] = value

    def reset_to_defaults(self) -> None:
        """Reset configuration to defaults"""
        self.config = self.DEFAULT_CONFIG.copy()
        self.save()
        print("✓ Reset configuration to defaults")

    def get_converter_config(self, converter_name: str) -> Dict[str, Any]:
        """
        Get configuration for specific converter

        Args:
            converter_name: Name of converter

        Returns:
            Converter configuration dict
        """
        converters = self.config.get('converters', {})
        return converters.get(converter_name, {})

    def set_converter_config(self, converter_name: str, config: Dict[str, Any]) -> None:
        """
        Set configuration for specific converter

        Args:
            converter_name: Name of converter
            config: Configuration dictionary
        """
        if 'converters' not in self.config:
            self.config['converters'] = {}

        self.config['converters'][converter_name] = config

    def export_config(self, filename: str) -> None:
        """
        Export configuration to file

        Args:
            filename: Output filename
        """
        with open(filename, 'w') as f:
            json.dump(self.config, f, indent=2)
        print(f"✓ Exported configuration to: {filename}")

    def import_config(self, filename: str) -> None:
        """
        Import configuration from file

        Args:
            filename: Input filename
        """
        with open(filename, 'r') as f:
            self.config = json.load(f)
        self.save()
        print(f"✓ Imported configuration from: {filename}")

    def validate_config(self) -> bool:
        """
        Validate configuration

        Returns:
            True if configuration is valid
        """
        required_keys = ['can_interface', 'dbc_file', 'log_directory']

        for key in required_keys:
            if key not in self.config:
                print(f"⚠ Missing required config key: {key}")
                return False

        return True

    def get_all(self) -> Dict[str, Any]:
        """
        Get entire configuration

        Returns:
            Configuration dictionary
        """
        return self.config.copy()
