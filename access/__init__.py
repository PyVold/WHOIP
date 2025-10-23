"""
Access control and authentication module.
Defines User and Application models, database, and authentication setup.
"""
from flask import Blueprint
from flask_login import LoginManager, UserMixin
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# Initialize database and authentication
db = SQLAlchemy()
login_manager = LoginManager()

# Create blueprint for access control routes
access_app = Blueprint('access', __name__, template_folder='templates', url_prefix='/myapi')


class User(UserMixin, db.Model):
    """
    User model for authentication and application ownership.

    Attributes:
        id: Primary key
        username: Unique username for login
        email: Unique email address
        password: Hashed password (pbkdf2:sha256)
        name: User's full name
        email_verified: Whether email has been verified
        email_verification_token: Token for email verification
        email_verification_sent_at: When verification email was sent
        password_reset_token: Token for password reset
        password_reset_sent_at: When reset email was sent
        last_login: Last successful login timestamp
        created_at: Account creation timestamp
        applications: One-to-many relationship with Application model
    """
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False, index=True)
    email = db.Column(db.String(100), unique=True, nullable=False, index=True)
    password = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(100), nullable=False)

    # Email verification
    email_verified = db.Column(db.Boolean, default=False)
    email_verification_token = db.Column(db.String(100), unique=True, index=True)
    email_verification_sent_at = db.Column(db.DateTime)

    # Password reset
    password_reset_token = db.Column(db.String(100), unique=True, index=True)
    password_reset_sent_at = db.Column(db.DateTime)

    # Tracking
    last_login = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    applications = db.relationship("Application", back_populates="user", lazy='dynamic', cascade="all, delete-orphan")

    def __repr__(self):
        return f'<User {self.username}>'

    @classmethod
    def lookup(cls, username):
        """
        Lookup user by username.

        Args:
            username: Username to search for

        Returns:
            User object or None if not found
        """
        return cls.query.filter_by(username=username).one_or_none()

    @classmethod
    def lookup_by_email(cls, email):
        """
        Lookup user by email.

        Args:
            email: Email to search for

        Returns:
            User object or None if not found
        """
        return cls.query.filter_by(email=email).first()

    def generate_verification_token(self):
        """
        Generate email verification token.

        Returns:
            Verification token
        """
        import secrets
        self.email_verification_token = secrets.token_urlsafe(32)
        self.email_verification_sent_at = datetime.utcnow()
        return self.email_verification_token

    def generate_reset_token(self):
        """
        Generate password reset token.

        Returns:
            Reset token
        """
        import secrets
        self.password_reset_token = secrets.token_urlsafe(32)
        self.password_reset_sent_at = datetime.utcnow()
        return self.password_reset_token

    def is_verification_token_valid(self, hours=24):
        """
        Check if email verification token is still valid.

        Args:
            hours: Hours until expiration (default: 24)

        Returns:
            True if valid
        """
        if not self.email_verification_sent_at:
            return False
        from datetime import timedelta
        expiry = self.email_verification_sent_at + timedelta(hours=hours)
        return datetime.utcnow() < expiry

    def is_reset_token_valid(self, hours=1):
        """
        Check if password reset token is still valid.

        Args:
            hours: Hours until expiration (default: 1)

        Returns:
            True if valid
        """
        if not self.password_reset_sent_at:
            return False
        from datetime import timedelta
        expiry = self.password_reset_sent_at + timedelta(hours=hours)
        return datetime.utcnow() < expiry


class Application(db.Model):
    """
    Application/API Token model for rate-limited API access.

    Attributes:
        id: Primary key
        app_name: Application name
        user_id: Foreign key to User
        user: Relationship back to User
        token: API authentication token
        calls_count: Number of API calls today
        date: Date of last counter reset (MM/DD/YY format)
        max_calls: Daily rate limit
        state: Token status (active, waiting approval, Not Active, deletion requested)
        created_at: Token creation timestamp
    """
    __tablename__ = 'application'

    id = db.Column(db.Integer, primary_key=True)
    app_name = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    user = db.relationship("User", back_populates="applications")
    token = db.Column(db.String(255), unique=True, nullable=False, index=True)
    calls_count = db.Column(db.Integer, default=0)
    date = db.Column(db.String(20))
    max_calls = db.Column(db.Integer, default=1000)
    state = db.Column(
        db.Enum('active', 'waiting approval', 'Not Active', 'deletion requested', name='token_status'),
        default='waiting approval',
        nullable=False
    )
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Application {self.app_name}>'

    @classmethod
    def lookup(cls, token):
        """
        Lookup application by token.

        Args:
            token: API token to search for

        Returns:
            Application object or None if not found
        """
        return cls.query.filter_by(token=token).first()

    @classmethod
    def identity(cls, id):
        """
        Lookup application by ID.

        Args:
            id: Application ID to search for

        Returns:
            Application object or None if not found
        """
        return cls.query.filter_by(id=id).first()


@login_manager.user_loader
def load_user(user_id):
    """
    Flask-Login user loader callback.

    Args:
        user_id: User ID from session

    Returns:
        User object or None if not found
    """
    return User.query.get(int(user_id))


# Import routes after models to avoid circular imports
from . import login, signup, delete, password_reset, analytics