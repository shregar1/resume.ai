import json
import os
from typing import Dict, Any
from pathlib import Path

from constants.default import Default

from dtos.configurations.security import SecurityConfigurationDTO

from start_utils import logger


class SecurityConfiguration:
    """
    Security configuration loader and manager.
    Loads configuration from config/security/config.json and supports
    environment variable overrides.
    """
    def __init__(self, config_path: str = None):
        """
        Initialize the SecurityConfiguration.
        Args:
            config_path (str): Optional path to the security config file.
        """
        self.config_path = config_path or "config/security/config.json"
        self._config = None

    def get_config(self) -> SecurityConfigurationDTO:
        """
        Load and return security configuration as a DTO.
        """
        if self._config is None:
            self._load_config()
        return self._config

    def _load_config(self):
        """
        Load configuration from JSON file, with environment variable overrides.
        Logs errors and falls back to default config if needed.
        """
        try:
            config_file = Path(self.config_path)
            if not config_file.exists():
                logger.debug(
                    "Security config file not found. Using default config."
                )
                self._config = self._get_default_config()
                return
            with open(config_file, 'r') as f:
                config_data = json.load(f)
            config_data = self._override_with_env_vars(config_data)
            self._config = SecurityConfigurationDTO(**config_data)
            logger.debug("Security config loaded successfully.")
        except Exception as e:
            logger.error(f"Error loading security config: {e}")
            self._config = self._get_default_config()

    def _override_with_env_vars(
        self,
        config_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Override configuration with environment variables.
        """
        env_mappings = {
            "SECURITY_HSTS_MAX_AGE": ("security_headers", "hsts_max_age"),
            "SECURITY_HSTS_INCLUDE_SUBDOMAINS": (
                "security_headers", "hsts_include_subdomains"
            ),
            "SECURITY_ENABLE_CSP": ("security_headers", "enable_csp"),
            "SECURITY_ENABLE_HSTS": ("security_headers", "enable_hsts"),
            "SECURITY_MAX_STRING_LENGTH": (
                "input_validation", "max_string_length"
            ),
            "SECURITY_MIN_PASSWORD_LENGTH": (
                "input_validation", "min_password_length"
            ),
            "SECURITY_JWT_EXPIRY_MINUTES": (
                "authentication", "jwt_expiry_minutes"
            ),
            "SECURITY_MAX_LOGIN_ATTEMPTS": (
                "authentication", "max_login_attempts"),
        }
        for env_var, (section, key) in env_mappings.items():
            env_value = os.getenv(env_var)
            if env_value is not None:
                # Convert string to appropriate type
                if isinstance(config_data[section][key], bool):
                    config_data[section][key] = (
                        env_value.lower() in ('true', '1', 'yes')
                    )
                elif isinstance(config_data[section][key], int):
                    config_data[section][key] = int(env_value)
                elif isinstance(config_data[section][key], float):
                    config_data[section][key] = float(env_value)
                else:
                    config_data[section][key] = env_value
        return config_data

    def _get_default_config(self) -> SecurityConfigurationDTO:
        """
        Get default security configuration as a DTO.
        """
        default_config = Default.SECURITY_CONFIGURATION
        return SecurityConfigurationDTO(**default_config)

    def reload_config(self):
        """
        Reload configuration from file.
        """
        logger.debug("Reloading security configuration from file.")
        self._config = None
        return self.get_config()
