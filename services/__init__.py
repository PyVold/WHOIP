"""
Services package for WHOIP application.
Contains email, caching, and other service modules.
"""
from .email_service import mail, send_email, send_password_reset_email, send_verification_email
from .cache_service import init_cache, cache_get, cache_set, get_cache_stats

__all__ = [
    'mail',
    'send_email',
    'send_password_reset_email',
    'send_verification_email',
    'init_cache',
    'cache_get',
    'cache_set',
    'get_cache_stats'
]
