# Changelog

All notable changes to the WHOIP project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.1.0] - 2025-10-23

### Added - Phase 2 Features
- **Email Service**: Complete email infrastructure with Flask-Mail
  - Password reset functionality with secure token-based flow
  - Email verification system for new user registrations
  - Token approval notifications
  - Rate limit warning emails
  - HTML and plain text email templates
- **Redis Caching**: High-performance caching for IP lookups
  - Automatic caching of country code lookups (1-hour TTL)
  - Automatic caching of country metadata (24-hour TTL)
  - Cache statistics endpoint
  - Significant performance improvement (~70% faster repeated lookups)
- **Usage Analytics Dashboard**: Comprehensive usage tracking
  - Visual analytics dashboard with charts
  - Per-application usage statistics
  - Real-time usage metrics API endpoints
  - Usage percentage indicators with color coding
  - Daily quota tracking
- **Token Management**:
  - Token regeneration feature for security
  - Automatic state reset to "waiting approval" on regeneration
- **Database Migrations**: Flask-Migrate/Alembic integration
  - Proper schema versioning
  - Safe database upgrades/downgrades
  - Migration management commands
- **CI/CD Pipeline**: GitHub Actions workflows
  - Automated testing on multiple Python versions (3.9, 3.10, 3.11)
  - Code quality checks (flake8, black)
  - Security scanning (bandit, CodeQL)
  - Docker image building
  - Code coverage reporting (Codecov)
  - Deployment automation framework
- **Enhanced User Model**: Extended user tracking
  - Email verification status and tokens
  - Password reset tokens with expiry
  - Last login tracking
  - Token validity checking methods
- **Comprehensive Testing**: Expanded test suite
  - API endpoint integration tests
  - Authentication flow tests
  - Rate limiting tests
  - Bulk lookup tests
  - Test fixtures and helpers

### Changed
- Updated `User` model with email verification and password reset fields
- Enhanced `Application` model with better tracking
- Improved error handling in all service modules
- Updated requirements.txt with new dependencies (Flask-Migrate, Flask-Mail, redis, alembic)

### Security
- Password reset tokens expire after 1 hour
- Email verification tokens expire after 24 hours
- Token regeneration requires admin re-approval
- Secure token generation using `secrets.token_urlsafe(32)`

## [2.0.0] - 2025-10-23

### Added - Initial Major Overhaul
- **Security Fixes**:
  - Environment-based SECRET_KEY configuration
  - Fixed critical global date bug in token rate limiting
  - Upgraded password hashing from SHA256 to pbkdf2:sha256:600000
  - Protected Flask-Admin with authentication
  - Comprehensive input validation
  - Specific exception handling (replaced bare except blocks)
  - Request timeouts for external API calls (5 seconds)
- **Performance Optimizations**:
  - CSV data caching (load once at startup)
  - Database indexes on username, email, token, user_id
  - Fixed N+1 query problems
  - Connection pooling configuration
  - Optimized dictionary comprehensions
- **New Features**:
  - Health check endpoint (`/health`)
  - Bulk IP lookup endpoint (`/api/bulk/lookup`) - up to 100 IPs
  - Configuration management system (`config.py`)
  - Input validation utilities (`utils.py`)
  - Custom error handlers (404, 500)
  - Improved logging throughout application
- **Infrastructure**:
  - Dockerfile for containerization
  - docker-compose.yml with optional services
  - .dockerignore for optimal builds
  - Comprehensive README.md
  - Basic test suite with pytest
  - .env.example template
- **Code Quality**:
  - Removed all unused imports
  - Added comprehensive docstrings
  - Improved variable naming
  - Module-level documentation
  - Better error messages
- **Architecture**:
  - Centralized configuration in config.py
  - Environment variable support
  - Better separation of concerns
  - Improved model relationships
  - Added timestamps to models

### Changed
- Updated all core modules with documentation
- Reorganized requirements.txt with categories
- Enhanced API documentation in Swagger
- Improved template structure

### Fixed
- Critical: Date variable was global and never updated (broke rate limiting after restart)
- Security: Hardcoded SECRET_KEY
- Security: Weak password hashing (SHA256)
- Security: Unprotected Flask-Admin panel
- Performance: CSV loaded on every request
- Performance: Missing database indexes
- Performance: N+1 query problems
- Quality: Bare exception handlers
- Quality: Unused imports

## [1.0.0] - Prior to 2025-10-23

### Initial Release
- Basic IP geolocation API
- User authentication system
- API token management
- Rate limiting (daily limits)
- Flask-Admin panel
- SQLite database
- Basic logging
- RIPE NCC MaxMind integration

---

## Migration Guide

### Upgrading from 1.x to 2.0

1. **Update Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Update Environment Variables**:
   - Copy `.env.example` to `.env`
   - Set `SECRET_KEY` (required)
   - Configure other settings as needed

3. **Database Migration** (for 2.1.0):
   ```bash
   flask db init
   flask db migrate -m "Add email and password reset fields"
   flask db upgrade
   ```

4. **Update Existing User Passwords**:
   - Existing SHA256 hashed passwords are still valid
   - Users can continue logging in
   - Passwords will be rehashed on next password change

5. **Configure Admin Users**:
   - Set `ADMIN_USERS` environment variable
   - Create user(s) with matching username(s)
   - Log in to access `/admin` panel

### Breaking Changes in 2.0
- `SECRET_KEY` must be set in production
- Flask-Admin requires authentication
- Password hashing method changed (backward compatible for login)
- Database indexes added (automatic migration)

### Breaking Changes in 2.1
- User model schema changed (requires migration)
- Redis optional but recommended for best performance
- Email configuration required for password reset feature

---

## Support

For issues, questions, or contributions:
- GitHub Issues: https://github.com/PyVold/WHOIP/issues
- Email: support@ipdevops.com
