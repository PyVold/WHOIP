"""
Simple smoke tests to ensure basic functionality.
"""
import pytest


def test_imports():
    """Test that basic imports work."""
    try:
        import flask
        import sqlalchemy
        import requests
        import pandas
        assert True
    except ImportError as e:
        pytest.fail(f"Import failed: {e}")


def test_python_version():
    """Test Python version."""
    import sys
    assert sys.version_info >= (3, 9), "Python 3.9+ required"


def test_basic_math():
    """Basic sanity test."""
    assert 1 + 1 == 2


def test_string_operations():
    """Test string operations."""
    test_str = "WHOIP"
    assert test_str.lower() == "whoip"
    assert len(test_str) == 5


class TestConfiguration:
    """Test configuration basics."""

    def test_config_import(self):
        """Test config module can be imported."""
        try:
            from config import Config
            assert Config is not None
        except ImportError:
            pytest.skip("Config module not available")

    def test_utils_import(self):
        """Test utils module can be imported."""
        try:
            from utils import validate_email
            assert validate_email is not None
        except ImportError:
            pytest.skip("Utils module not available")


class TestUtils:
    """Test utility functions."""

    def test_email_validation(self):
        """Test email validation function."""
        try:
            from utils import validate_email

            # Valid emails
            assert validate_email('test@example.com') is True
            assert validate_email('user.name@domain.co.uk') is True

            # Invalid emails
            assert validate_email('') is False
            assert validate_email('invalid') is False
            assert validate_email('@example.com') is False
        except ImportError:
            pytest.skip("Utils module not available")

    def test_password_validation(self):
        """Test password validation function."""
        try:
            from utils import validate_password

            config = {
                'MIN_PASSWORD_LENGTH': 8,
                'REQUIRE_PASSWORD_UPPERCASE': True,
                'REQUIRE_PASSWORD_LOWERCASE': True,
                'REQUIRE_PASSWORD_DIGIT': True,
                'REQUIRE_PASSWORD_SPECIAL': False
            }

            is_valid, msg = validate_password('Password123', config)
            assert is_valid is True

            is_valid, msg = validate_password('weak', config)
            assert is_valid is False
        except ImportError:
            pytest.skip("Utils module not available")
