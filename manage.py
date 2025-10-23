"""
Database migration management using Flask-Migrate.
"""
from flask_migrate import Migrate
from access import db
from app import app

# Initialize Flask-Migrate
migrate = Migrate(app, db)

if __name__ == '__main__':
    print("Database migration manager initialized.")
    print("Available commands:")
    print("  flask db init       - Initialize migrations directory")
    print("  flask db migrate    - Generate new migration")
    print("  flask db upgrade    - Apply migrations")
    print("  flask db downgrade  - Rollback migration")
    print("  flask db history    - Show migration history")
    print("  flask db current    - Show current revision")
