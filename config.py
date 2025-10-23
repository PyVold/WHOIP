"""
Configuration management for WHOIP application.
Loads settings from environment variables with sensible defaults.
"""
import os
import secrets
from datetime import timedelta


class Config:
    """Base configuration class."""

    # Flask Core Settings
    SECRET_KEY = os.getenv('SECRET_KEY', secrets.token_hex(32))
    DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'

    # Database Configuration
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL',
        f'sqlite:///{os.path.join(BASE_DIR, "lite2.db")}'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
    }

    # Flask-Admin Settings
    FLASK_ADMIN_SWATCH = os.getenv('FLASK_ADMIN_SWATCH', 'cerulean')

    # API Settings
    SWAGGER_UI_DOC_EXPANSION = 'list'
    API_TITLE = 'IPDevOps WHOIS'
    API_VERSION = '2.0'
    API_DESCRIPTION = 'IP Geolocation and WHOIS service with rate limiting'

    # Application Limits
    MAX_APPS_PER_USER = int(os.getenv('MAX_APPS_PER_USER', '3'))
    DEFAULT_RATE_LIMIT = int(os.getenv('DEFAULT_RATE_LIMIT', '1000'))

    # External API Configuration
    RIPE_API_URL = os.getenv(
        'RIPE_API_URL',
        'https://stat.ripe.net/data/maxmind-geo-lite/data.json'
    )
    RIPE_API_TIMEOUT = int(os.getenv('RIPE_API_TIMEOUT', '5'))

    # Security Settings
    SESSION_COOKIE_SECURE = os.getenv('SESSION_COOKIE_SECURE', 'False').lower() == 'true'
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)

    # Password Requirements
    MIN_PASSWORD_LENGTH = int(os.getenv('MIN_PASSWORD_LENGTH', '8'))
    REQUIRE_PASSWORD_UPPERCASE = os.getenv('REQUIRE_PASSWORD_UPPERCASE', 'True').lower() == 'true'
    REQUIRE_PASSWORD_LOWERCASE = os.getenv('REQUIRE_PASSWORD_LOWERCASE', 'True').lower() == 'true'
    REQUIRE_PASSWORD_DIGIT = os.getenv('REQUIRE_PASSWORD_DIGIT', 'True').lower() == 'true'
    REQUIRE_PASSWORD_SPECIAL = os.getenv('REQUIRE_PASSWORD_SPECIAL', 'False').lower() == 'true'

    # Logging Configuration
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_DIR = os.path.join(BASE_DIR, 'logs')

    # Cache Configuration
    CACHE_TYPE = os.getenv('CACHE_TYPE', 'simple')  # 'simple', 'redis', 'memcached'
    CACHE_REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    CACHE_DEFAULT_TIMEOUT = int(os.getenv('CACHE_TIMEOUT', '3600'))

    # Rate Limiting (global)
    RATELIMIT_ENABLED = os.getenv('RATELIMIT_ENABLED', 'True').lower() == 'true'
    RATELIMIT_STORAGE_URL = os.getenv('REDIS_URL', 'memory://')

    # Email Configuration (for future features)
    MAIL_SERVER = os.getenv('MAIL_SERVER', 'localhost')
    MAIL_PORT = int(os.getenv('MAIL_PORT', '587'))
    MAIL_USE_TLS = os.getenv('MAIL_USE_TLS', 'True').lower() == 'true'
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.getenv('MAIL_DEFAULT_SENDER', 'noreply@ipdevops.com')

    # Admin Users (comma-separated usernames)
    ADMIN_USERS = os.getenv('ADMIN_USERS', 'admin').split(',')


class DevelopmentConfig(Config):
    """Development environment configuration."""
    DEBUG = True
    SQLALCHEMY_ECHO = True


class ProductionConfig(Config):
    """Production environment configuration."""
    DEBUG = False
    SESSION_COOKIE_SECURE = True

    # Enforce environment variables in production
    @classmethod
    def validate(cls):
        required = ['SECRET_KEY', 'DATABASE_URL']
        missing = [key for key in required if not os.getenv(key)]
        if missing:
            raise ValueError(f"Missing required environment variables: {', '.join(missing)}")


class TestingConfig(Config):
    """Testing environment configuration."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False


# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}


def get_config():
    """Get configuration based on FLASK_ENV environment variable."""
    env = os.getenv('FLASK_ENV', 'development')
    return config.get(env, config['default'])
