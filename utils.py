"""
Utility functions for WHOIP application.
"""
import re
from typing import Tuple


def validate_email(email: str) -> bool:
    """
    Validate email address format.

    Args:
        email: Email address to validate

    Returns:
        True if email is valid, False otherwise
    """
    if not email:
        return False

    # Basic email regex pattern
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_password(password: str, config=None) -> Tuple[bool, str]:
    """
    Validate password against security requirements.

    Args:
        password: Password to validate
        config: Flask config object with password requirements

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not password:
        return False, "Password is required"

    # Default requirements
    min_length = 8
    require_uppercase = True
    require_lowercase = True
    require_digit = True
    require_special = False

    # Use config if provided
    if config:
        min_length = config.get('MIN_PASSWORD_LENGTH', 8)
        require_uppercase = config.get('REQUIRE_PASSWORD_UPPERCASE', True)
        require_lowercase = config.get('REQUIRE_PASSWORD_LOWERCASE', True)
        require_digit = config.get('REQUIRE_PASSWORD_DIGIT', True)
        require_special = config.get('REQUIRE_PASSWORD_SPECIAL', False)

    # Check minimum length
    if len(password) < min_length:
        return False, f"Password must be at least {min_length} characters long"

    # Check for uppercase letter
    if require_uppercase and not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"

    # Check for lowercase letter
    if require_lowercase and not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"

    # Check for digit
    if require_digit and not re.search(r'\d', password):
        return False, "Password must contain at least one digit"

    # Check for special character
    if require_special and not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False, "Password must contain at least one special character"

    return True, ""


def validate_username(username: str) -> Tuple[bool, str]:
    """
    Validate username format.

    Args:
        username: Username to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not username:
        return False, "Username is required"

    if len(username) < 3:
        return False, "Username must be at least 3 characters long"

    if len(username) > 50:
        return False, "Username must be less than 50 characters"

    # Allow alphanumeric, underscore, and hyphen
    if not re.match(r'^[a-zA-Z0-9_-]+$', username):
        return False, "Username can only contain letters, numbers, underscores, and hyphens"

    return True, ""


def validate_app_name(app_name: str) -> Tuple[bool, str]:
    """
    Validate application name format.

    Args:
        app_name: Application name to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not app_name:
        return False, "Application name is required"

    if len(app_name) < 3:
        return False, "Application name must be at least 3 characters long"

    if len(app_name) > 100:
        return False, "Application name must be less than 100 characters"

    # Allow alphanumeric, spaces, underscores, and hyphens
    if not re.match(r'^[a-zA-Z0-9 _-]+$', app_name):
        return False, "Application name can only contain letters, numbers, spaces, underscores, and hyphens"

    return True, ""


def sanitize_string(value: str, max_length: int = 1000) -> str:
    """
    Sanitize string input by trimming and limiting length.

    Args:
        value: String to sanitize
        max_length: Maximum allowed length

    Returns:
        Sanitized string
    """
    if not value:
        return ""

    # Strip whitespace
    value = value.strip()

    # Limit length
    if len(value) > max_length:
        value = value[:max_length]

    return value
