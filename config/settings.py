"""
Configuration module for WAR KRS ITERA Automation
"""

import json
import os
from typing import Dict, Any
from pathlib import Path
from dotenv import load_dotenv


class Config:
    """Configuration class following SOLID principles"""
    
    def __init__(self, config_file: str = "config.json"):
        # Load environment variables from .env file
        load_dotenv()
        
        self.config_file = config_file
        
        # Handle relative vs absolute paths
        if config_file.startswith('/') or config_file.startswith('\\'):
            # Absolute path
            self.config_path = Path(config_file)
        elif '/' in config_file or '\\' in config_file:
            # Relative path from project root
            self.config_path = Path.cwd() / config_file
        else:
            # Just filename, look in config directory
            self.config_path = Path(__file__).parent / config_file
            
        self.data = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from JSON file and merge with environment variables"""
        # Start with default config (includes env vars)
        config = self._get_default_config()
        
        # If JSON config file exists, merge it
        if self.config_path.exists():
            with open(self.config_path, 'r', encoding='utf-8') as f:
                json_config = json.load(f)
                config = self._merge_configs(config, json_config)
        
        # Override with environment variables if they exist
        config = self._apply_env_overrides(config)
        
        return config
    
    def _merge_configs(self, base_config: Dict[str, Any], override_config: Dict[str, Any]) -> Dict[str, Any]:
        """Recursively merge two configuration dictionaries"""
        result = base_config.copy()
        
        for key, value in override_config.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_configs(result[key], value)
            else:
                result[key] = value
        
        return result
    
    def _apply_env_overrides(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Apply environment variable overrides to configuration"""
        # Override cookies if env vars are set
        if os.getenv("CI_SESSION"):
            config["cookies"]["ci_session"] = os.getenv("CI_SESSION")
        if os.getenv("CF_CLEARANCE"):
            config["cookies"]["cf_clearance"] = os.getenv("CF_CLEARANCE")
        
        # Override settings if env vars are set
        if os.getenv("DELAY_SECONDS"):
            config["settings"]["delay_seconds"] = int(os.getenv("DELAY_SECONDS"))
        if os.getenv("REQUEST_TIMEOUT"):
            config["settings"]["request_timeout"] = int(os.getenv("REQUEST_TIMEOUT"))
        
        # Add Telegram configuration
        if "telegram" not in config:
            config["telegram"] = {}
        
        if os.getenv("TELEGRAM_BOT_TOKEN"):
            config["telegram"]["bot_token"] = os.getenv("TELEGRAM_BOT_TOKEN")
        if os.getenv("TELEGRAM_CHAT_ID"):
            config["telegram"]["chat_id"] = os.getenv("TELEGRAM_CHAT_ID")
        
        return config
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration with environment variable support"""
        return {
            "cookies": {
                "ci_session": os.getenv("CI_SESSION", "GANTI_DENGAN_SESSION_ANDA"),
                "cf_clearance": os.getenv("CF_CLEARANCE", "GANTI_DENGAN_CLEARANCE_ANDA")
            },
            "target_courses": {
            },
            "settings": {
                "delay_seconds": int(os.getenv("DELAY_SECONDS", "45")),
                "request_timeout": int(os.getenv("REQUEST_TIMEOUT", "20")),
                "verification_delay": 2,
                "inter_request_delay": 2
            },
            "urls": {
                "pilih_mk": "https://siakad.itera.ac.id/mahasiswa/krsbaru/pilihmk",
                "simpan_krs": "https://siakad.itera.ac.id/mahasiswa/krsbaru/simpanKRS"
            }
        }
    
    def save_config(self) -> None:
        """Save current configuration to file"""
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, indent=4, ensure_ascii=False)
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by key (supports dot notation)"""
        keys = key.split('.')
        value = self.data
        
        try:
            for k in keys:
                value = value[k]
            return value
        except KeyError:
            return default
    
    def set(self, key: str, value: Any) -> None:
        """Set configuration value by key (supports dot notation)"""
        keys = key.split('.')
        config = self.data
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
    
    def is_configured(self) -> bool:
        """Check if cookies are properly configured"""
        ci_session = self.get('cookies.ci_session', '')
        cf_clearance = self.get('cookies.cf_clearance', '')
        
        return (
            ci_session and ci_session != "GANTI_DENGAN_SESSION_ANDA" and
            cf_clearance and cf_clearance != "GANTI_DENGAN_CLEARANCE_ANDA"
        )
    
    @property
    def cookies(self) -> Dict[str, str]:
        """Get cookies configuration"""
        return self.get('cookies', {})
    
    @property
    def target_courses(self) -> Dict[str, str]:
        """Get target courses configuration"""
        return self.get('target_courses', {})
    
    @property
    def urls(self) -> Dict[str, str]:
        """Get URLs configuration"""
        return self.get('urls', {})
    
    @property
    def settings(self) -> Dict[str, Any]:
        """Get general settings"""
        return self.get('settings', {})
    
    @property
    def telegram(self) -> Dict[str, str]:
        """Get Telegram configuration"""
        return self.get('telegram', {})
    
    def get_all(self) -> Dict[str, Any]:
        """Get all configuration data formatted for controller"""
        return {
            'siakad_urls': self.urls,
            'cycle_delay': self.settings.get('delay_seconds', 45),
            'inter_request_delay': self.settings.get('inter_request_delay', 2),
            'request_timeout': self.settings.get('request_timeout', 20),
            'verification_delay': self.settings.get('verification_delay', 2)
        }
