"""
API Token authentication and rate limiting decorator.
"""
from functools import wraps
from flask import request
from flask_login import current_user
from access import User, Application, db
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


def token_required(f):
    """
    Decorator to require and validate API token authentication.

    Checks X-API-KEY header for valid token and enforces daily rate limits.
    Rate limits reset at midnight based on current date.

    Returns:
        401: If token is missing, invalid, inactive, or rate limit exceeded
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        # Get current date for rate limit reset
        today = datetime.today().strftime("%m/%d/%y")

        token = None
        if 'X-API-KEY' in request.headers:
            token = request.headers['X-API-KEY']

            # Validate token exists in database
            tokencheck = Application.lookup(token=token)
            if not tokencheck:
                logger.warning(f"Unrecognized token attempted: {token[:8]}...")
                return {'message': 'Token is not recognized'}, 401

            # Check token is active
            if tokencheck.state != 'active':
                logger.warning(f"Inactive token attempted: {tokencheck.app_name} (state: {tokencheck.state})")
                return {'message': 'Token is either disabled or needs approval!'}, 401

            # Reset counter if it's a new day
            if tokencheck.date != today:
                logger.info(f"Resetting daily counter for {tokencheck.app_name}")
                tokencheck.date = today
                tokencheck.calls_count = 0

            # Check rate limit
            elif tokencheck.date == today and tokencheck.calls_count >= tokencheck.max_calls:
                logger.warning(f"Rate limit exceeded for {tokencheck.app_name}: {tokencheck.calls_count}/{tokencheck.max_calls}")
                return {
                    'message': f'Max calls of {tokencheck.max_calls} reached for today, try again tomorrow!',
                    'limit': tokencheck.max_calls,
                    'reset_time': 'midnight UTC'
                }, 401

            # Increment call counter
            tokencheck.calls_count += 1
            try:
                db.session.commit()
            except Exception as e:
                logger.error(f"Failed to update call counter: {e}")
                db.session.rollback()

        if not token:
            return {
                'message': 'Authorization required to run this call',
                'documentation': 'https://ipdevops.com/myapi/tokens'
            }, 401

        return f(*args, **kwargs)
    return decorated
