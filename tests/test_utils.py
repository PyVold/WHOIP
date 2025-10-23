"""
Unit tests for utility functions.
"""
import pytest
from utils import validate_email, validate_password, validate_username, validate_app_name, sanitize_string


class TestEmailValidation:
    """Test email validation function."""

    def test_valid_emails(self):
        assert validate_email('user@example.com') is True
        assert validate_email('test.user@domain.co.uk') is True
        assert validate_email('user+tag@example.com') is True

    def test_invalid_emails(self):
        assert validate_email('') is False
        assert validate_email('invalid') is False
        assert validate_email('@example.com') is False
        assert validate_email('user@') is False
        assert validate_email('user @example.com') is False


class TestPasswordValidation:
    """Test password validation function."""

    def test_valid_passwords(self):
        config = {
            'MIN_PASSWORD_LENGTH': 8,
            'REQUIRE_PASSWORD_UPPERCASE': True,
            'REQUIRE_PASSWORD_LOWERCASE': True,
            'REQUIRE_PASSWORD_DIGIT': True,
            'REQUIRE_PASSWORD_SPECIAL': False
        }
        is_valid, msg = validate_password('Password123', config)
        assert is_valid is True
        assert msg == ''

    def test_too_short(self):
        config = {'MIN_PASSWORD_LENGTH': 8}
        is_valid, msg = validate_password('Pass1', config)
        assert is_valid is False
        assert 'at least 8 characters' in msg

    def test_missing_uppercase(self):
        config = {
            'MIN_PASSWORD_LENGTH': 8,
            'REQUIRE_PASSWORD_UPPERCASE': True
        }
        is_valid, msg = validate_password('password123', config)
        assert is_valid is False
        assert 'uppercase' in msg

    def test_missing_digit(self):
        config = {
            'MIN_PASSWORD_LENGTH': 8,
            'REQUIRE_PASSWORD_DIGIT': True
        }
        is_valid, msg = validate_password('Password', config)
        assert is_valid is False
        assert 'digit' in msg


class TestUsernameValidation:
    """Test username validation function."""

    def test_valid_usernames(self):
        assert validate_username('john_doe')[0] is True
        assert validate_username('user123')[0] is True
        assert validate_username('test-user')[0] is True

    def test_too_short(self):
        is_valid, msg = validate_username('ab')
        assert is_valid is False
        assert 'at least 3 characters' in msg

    def test_too_long(self):
        is_valid, msg = validate_username('a' * 51)
        assert is_valid is False
        assert 'less than 50 characters' in msg

    def test_invalid_characters(self):
        is_valid, msg = validate_username('user@name')
        assert is_valid is False
        assert 'letters, numbers, underscores' in msg


class TestAppNameValidation:
    """Test application name validation function."""

    def test_valid_app_names(self):
        assert validate_app_name('My Application')[0] is True
        assert validate_app_name('App_123')[0] is True
        assert validate_app_name('Test-App')[0] is True

    def test_too_short(self):
        is_valid, msg = validate_app_name('ab')
        assert is_valid is False
        assert 'at least 3 characters' in msg

    def test_invalid_characters(self):
        is_valid, msg = validate_app_name('App@Name!')
        assert is_valid is False


class TestSanitization:
    """Test string sanitization function."""

    def test_trim_whitespace(self):
        assert sanitize_string('  test  ') == 'test'
        assert sanitize_string('\ttest\n') == 'test'

    def test_length_limit(self):
        long_string = 'a' * 2000
        result = sanitize_string(long_string, max_length=1000)
        assert len(result) == 1000

    def test_empty_string(self):
        assert sanitize_string('') == ''
        assert sanitize_string('   ') == ''
