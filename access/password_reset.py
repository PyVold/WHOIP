"""
Password reset functionality.
"""
from flask import render_template, request, redirect, url_for, flash
from werkzeug.security import generate_password_hash
from . import access_app
from . import User, db
from services.email_service import send_password_reset_email
from utils import validate_password, sanitize_string
import logging

logger = logging.getLogger(__name__)


@access_app.route('/forgot-password/', methods=['GET', 'POST'])
def forgot_password():
    """
    Request password reset link.

    GET: Display forgot password form
    POST: Send reset email
    """
    if request.method == 'GET':
        return render_template('forgot_password.html')

    # Get email from form
    email = sanitize_string(request.form.get('email', ''), 100)

    if not email:
        flash('Please enter your email address.')
        return redirect(url_for('access.forgot_password'))

    # Look up user
    user = User.lookup_by_email(email)

    # Always show success message (don't reveal if email exists)
    flash('If an account exists with that email, a password reset link has been sent.')

    if user:
        try:
            # Generate reset token
            reset_token = user.generate_reset_token()
            db.session.commit()

            # Send email
            send_password_reset_email(user, reset_token)
            logger.info(f"Password reset email sent to: {email}")

        except Exception as e:
            logger.error(f"Error sending password reset email: {e}")
            db.session.rollback()

    return redirect(url_for('access.login'))


@access_app.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    """
    Reset password with token.

    GET: Display reset password form
    POST: Update password
    """
    # Find user by token
    user = User.query.filter_by(password_reset_token=token).first()

    if not user:
        flash('Invalid or expired reset link.')
        return redirect(url_for('access.login'))

    # Check if token is still valid (1 hour)
    if not user.is_reset_token_valid(hours=1):
        flash('This reset link has expired. Please request a new one.')
        return redirect(url_for('access.forgot_password'))

    if request.method == 'GET':
        return render_template('reset_password.html', token=token)

    # Process password reset
    password = request.form.get('password', '')
    password_confirm = request.form.get('password_confirm', '')

    # Validate password
    from flask import current_app
    is_valid, error_msg = validate_password(password, current_app.config)
    if not is_valid:
        flash(error_msg)
        return redirect(url_for('access.reset_password', token=token))

    # Check passwords match
    if password != password_confirm:
        flash('Passwords do not match.')
        return redirect(url_for('access.reset_password', token=token))

    try:
        # Update password
        user.password = generate_password_hash(
            password,
            method='pbkdf2:sha256:600000'
        )

        # Clear reset token
        user.password_reset_token = None
        user.password_reset_sent_at = None

        db.session.commit()

        logger.info(f"Password reset successful for user: {user.username}")
        flash('Your password has been reset successfully. Please log in.')
        return redirect(url_for('access.login'))

    except Exception as e:
        db.session.rollback()
        logger.error(f"Error resetting password: {e}")
        flash('An error occurred. Please try again.')
        return redirect(url_for('access.reset_password', token=token))


@access_app.route('/verify-email/<token>')
def verify_email(token):
    """
    Verify user email with token.

    Args:
        token: Email verification token
    """
    # Find user by token
    user = User.query.filter_by(email_verification_token=token).first()

    if not user:
        flash('Invalid verification link.')
        return redirect(url_for('access.login'))

    # Check if already verified
    if user.email_verified:
        flash('Your email is already verified. Please log in.')
        return redirect(url_for('access.login'))

    # Check if token is still valid (24 hours)
    if not user.is_verification_token_valid(hours=24):
        flash('This verification link has expired. Please contact support.')
        return redirect(url_for('access.login'))

    try:
        # Mark as verified
        user.email_verified = True
        user.email_verification_token = None
        user.email_verification_sent_at = None

        db.session.commit()

        logger.info(f"Email verified for user: {user.username}")
        flash('Your email has been verified! You can now log in.')
        return redirect(url_for('access.login'))

    except Exception as e:
        db.session.rollback()
        logger.error(f"Error verifying email: {e}")
        flash('An error occurred. Please try again.')
        return redirect(url_for('access.login'))


@access_app.route('/resend-verification/', methods=['POST'])
def resend_verification():
    """
    Resend verification email.
    """
    from flask_login import current_user, login_required

    if not current_user.is_authenticated:
        flash('Please log in first.')
        return redirect(url_for('access.login'))

    if current_user.email_verified:
        flash('Your email is already verified.')
        return redirect(url_for('access.tokens'))

    try:
        from services.email_service import send_verification_email

        # Generate new token
        token = current_user.generate_verification_token()
        db.session.commit()

        # Send email
        send_verification_email(current_user, token)

        logger.info(f"Verification email resent to: {current_user.email}")
        flash('Verification email sent! Please check your inbox.')

    except Exception as e:
        logger.error(f"Error resending verification email: {e}")
        flash('An error occurred. Please try again later.')

    return redirect(url_for('access.tokens'))
