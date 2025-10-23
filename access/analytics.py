"""
Usage analytics dashboard for API tokens.
"""
from flask import render_template, jsonify
from flask_login import login_required, current_user
from . import access_app
from . import Application, db
from sqlalchemy import func
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


@access_app.route('/analytics/')
@login_required
def analytics():
    """
    Display analytics dashboard for user's API tokens.
    """
    # Get user's applications
    apps = current_user.applications.all()

    # Calculate totals
    total_apps = len(apps)
    active_apps = sum(1 for app in apps if app.state == 'active')
    total_calls_today = sum(app.calls_count for app in apps)
    total_quota = sum(app.max_calls for app in apps)

    return render_template(
        'analytics.html',
        apps=apps,
        total_apps=total_apps,
        active_apps=active_apps,
        total_calls_today=total_calls_today,
        total_quota=total_quota
    )


@access_app.route('/analytics/api/usage-summary')
@login_required
def api_usage_summary():
    """
    API endpoint for usage summary data.

    Returns:
        JSON with usage statistics
    """
    apps = current_user.applications.all()

    data = {
        'total_applications': len(apps),
        'active_applications': sum(1 for app in apps if app.state == 'active'),
        'pending_applications': sum(1 for app in apps if app.state == 'waiting approval'),
        'total_calls_today': sum(app.calls_count for app in apps),
        'total_daily_quota': sum(app.max_calls for app in apps),
        'applications': [
            {
                'id': app.id,
                'name': app.app_name,
                'state': app.state,
                'calls_today': app.calls_count,
                'daily_limit': app.max_calls,
                'usage_percent': round((app.calls_count / app.max_calls * 100), 2) if app.max_calls > 0 else 0,
                'created_at': app.created_at.isoformat() if app.created_at else None
            }
            for app in apps
        ]
    }

    return jsonify(data)


@access_app.route('/analytics/api/app/<int:app_id>/stats')
@login_required
def api_app_stats(app_id):
    """
    Get detailed statistics for a specific application.

    Args:
        app_id: Application ID

    Returns:
        JSON with app statistics
    """
    app = Application.identity(app_id)

    if not app or app.user_id != current_user.id:
        return jsonify({'error': 'Application not found'}), 404

    data = {
        'id': app.id,
        'name': app.app_name,
        'token': app.token[:16] + '...' if len(app.token) > 16 else app.token,
        'state': app.state,
        'calls_today': app.calls_count,
        'daily_limit': app.max_calls,
        'usage_percent': round((app.calls_count / app.max_calls * 100), 2) if app.max_calls > 0 else 0,
        'created_at': app.created_at.isoformat() if app.created_at else None,
        'last_reset': app.date,
        'remaining_calls': max(0, app.max_calls - app.calls_count)
    }

    return jsonify(data)


@access_app.route('/regenerate-token/<int:app_id>', methods=['POST'])
@login_required
def regenerate_token(app_id):
    """
    Regenerate API token for an application.

    Args:
        app_id: Application ID
    """
    from flask import flash, redirect, url_for
    import secrets

    app = Application.identity(app_id)

    if not app or app.user_id != current_user.id:
        flash('Application not found.')
        return redirect(url_for('access.tokens'))

    try:
        # Generate new token
        old_token = app.token[:16]
        app.token = secrets.token_hex(32)

        # Reset state to waiting approval for security
        app.state = 'waiting approval'
        app.calls_count = 0

        db.session.commit()

        logger.info(f"Token regenerated for app {app.app_name} by user {current_user.username}")
        flash(f'Token for "{app.app_name}" has been regenerated. New token is pending approval.')

    except Exception as e:
        db.session.rollback()
        logger.error(f"Error regenerating token: {e}")
        flash('An error occurred. Please try again.')

    return redirect(url_for('access.tokens'))
