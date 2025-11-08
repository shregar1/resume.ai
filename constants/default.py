"""
Default configuration constants for the application.
"""
from typing import Any, Dict, Final


class Default:
    """
    Default values for application configuration, including rate limiting,
    security, authentication, and CORS settings.
    """
    ACCESS_TOKEN_EXPIRE_MINUTES: Final[int] = 1440
    RATE_LIMIT_MAX_REQUESTS: Final[int] = 2
    RATE_LIMIT_WINDOW_SECONDS: Final[int] = 60
    RATE_LIMIT_REQUESTS_PER_MINUTE: Final[int] = 60
    RATE_LIMIT_REQUESTS_PER_HOUR: Final[int] = 1000
    RATE_LIMIT_BURST_LIMIT: Final[int] = 10
    SECURITY_CONFIGURATION: Final[Dict[str, Any]] = {
            "rate_limiting": {
                "requests_per_minute": 60,
                "requests_per_hour": 1000,
                "burst_limit": 10,
                "window_size": 60,
                "enable_sliding_window": True,
                "enable_token_bucket": False,
                "enable_fixed_window": False,
                "excluded_paths": ["/health", "/docs", "/openapi.json"],
                "excluded_methods": ["OPTIONS"]
            },
            "security_headers": {
                "enable_hsts": True,
                "enable_csp": True,
                "csp_report_only": False,
                "hsts_max_age": 31536000,
                "hsts_include_subdomains": True,
                "hsts_preload": False,
                "frame_options": "DENY",
                "content_type_options": "nosniff",
                "xss_protection": "1; mode=block",
                "referrer_policy": "strict-origin-when-cross-origin",
                "custom_csp": None,
                "custom_permissions_policy": None
            },
            "input_validation": {
                "max_string_length": 1000,
                "max_password_length": 128,
                "min_password_length": 8,
                "max_email_length": 254,
                "enable_sql_injection_check": True,
                "enable_xss_check": True,
                "enable_path_traversal_check": True,
                "weak_passwords": [
                    "password", "123456", "qwerty", "admin", "letmein"
                ]
            },
            "authentication": {
                "jwt_expiry_minutes": 30,
                "refresh_token_expiry_days": 7,
                "max_login_attempts": 5,
                "lockout_duration_minutes": 15,
                "password_history_count": 5,
                "require_strong_password": True,
                "session_timeout_minutes": 60
            },
            "cors": {
                "allowed_origins": ["*"],
                "allowed_methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
                "allowed_headers": ["*"],
                "allow_credentials": True,
                "max_age": 3600
            }
        }
