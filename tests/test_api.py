"""
Integration tests for API endpoints.
"""
import pytest
import json
from app import app as flask_app
from access import db, User, Application


@pytest.fixture
def app():
    """Create application for testing."""
    flask_app.config['TESTING'] = True
    flask_app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    flask_app.config['WTF_CSRF_ENABLED'] = False

    with flask_app.app_context():
        db.create_all()
        yield flask_app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()


@pytest.fixture
def test_user(app):
    """Create test user."""
    from werkzeug.security import generate_password_hash

    user = User(
        username='testuser',
        email='test@example.com',
        password=generate_password_hash('Password123', method='pbkdf2:sha256:600000'),
        name='Test User',
        email_verified=True
    )
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture
def test_token(app, test_user):
    """Create test API token."""
    import secrets

    token_value = secrets.token_hex(32)
    app_token = Application(
        app_name='Test App',
        user_id=test_user.id,
        token=token_value,
        state='active',
        max_calls=1000
    )
    db.session.add(app_token)
    db.session.commit()
    return token_value


class TestHealthEndpoint:
    """Test health check endpoint."""

    def test_health_check(self, client):
        response = client.get('/health')
        assert response.status_code == 200

        data = json.loads(response.data)
        assert data['status'] == 'healthy'
        assert 'version' in data
        assert 'timestamp' in data


class TestMyIPEndpoint:
    """Test my IP address lookup endpoint."""

    def test_my_ip_lookup(self, client):
        response = client.get('/api/whoip/myip/')
        assert response.status_code == 200

        data = json.loads(response.data)
        assert 'ip' in data
        assert 'country' in data
        assert 'code' in data


class TestRemoteIPEndpoint:
    """Test remote IP address lookup endpoint."""

    def test_valid_ip_lookup(self, client):
        response = client.get('/api/whoip/remip/8.8.8.8')
        assert response.status_code == 200

        data = json.loads(response.data)
        assert data['ip'] == '8.8.8.8'
        assert 'country' in data
        assert 'code' in data

    def test_invalid_ip_lookup(self, client):
        response = client.get('/api/whoip/remip/invalid')
        assert response.status_code == 400

        data = json.loads(response.data)
        assert 'error' in data


class TestBulkLookupEndpoint:
    """Test bulk IP lookup endpoint."""

    def test_bulk_lookup_requires_auth(self, client):
        response = client.post(
            '/api/bulk/lookup',
            data=json.dumps({'ips': ['8.8.8.8']}),
            content_type='application/json'
        )
        assert response.status_code == 401

    def test_bulk_lookup_with_token(self, client, test_token):
        response = client.post(
            '/api/bulk/lookup',
            data=json.dumps({'ips': ['8.8.8.8', '1.1.1.1']}),
            headers={'X-API-KEY': test_token},
            content_type='application/json'
        )
        assert response.status_code == 200

        data = json.loads(response.data)
        assert data['total'] == 2
        assert len(data['results']) == 2

    def test_bulk_lookup_limit(self, client, test_token):
        # Test max 100 IPs
        ips = [f'1.1.1.{i}' for i in range(101)]
        response = client.post(
            '/api/bulk/lookup',
            data=json.dumps({'ips': ips}),
            headers={'X-API-KEY': test_token},
            content_type='application/json'
        )
        assert response.status_code == 400

        data = json.loads(response.data)
        assert 'Maximum 100' in data['message']


class TestAuthentication:
    """Test user authentication."""

    def test_login_page(self, client):
        response = client.get('/myapi/login/')
        assert response.status_code == 200

    def test_signup_page(self, client):
        response = client.get('/myapi/signup/')
        assert response.status_code == 200

    def test_successful_login(self, client, test_user):
        response = client.post('/myapi/login/', data={
            'username': 'testuser',
            'password': 'Password123'
        }, follow_redirects=True)
        assert response.status_code == 200

    def test_failed_login(self, client, test_user):
        response = client.post('/myapi/login/', data={
            'username': 'testuser',
            'password': 'wrongpassword'
        }, follow_redirects=True)
        assert response.status_code == 200
        # Should redirect back to login


class TestRateLimiting:
    """Test API rate limiting."""

    def test_rate_limit_enforcement(self, client, test_token, app):
        # Set low limit for testing
        with app.app_context():
            token = Application.lookup(test_token)
            token.max_calls = 2
            token.calls_count = 0
            from datetime import datetime
            token.date = datetime.today().strftime("%m/%d/%y")
            db.session.commit()

        # First two requests should succeed
        for i in range(2):
            response = client.post(
                '/api/bulk/lookup',
                data=json.dumps({'ips': ['8.8.8.8']}),
                headers={'X-API-KEY': test_token},
                content_type='application/json'
            )
            assert response.status_code == 200

        # Third request should be rate limited
        response = client.post(
            '/api/bulk/lookup',
            data=json.dumps({'ips': ['8.8.8.8']}),
            headers={'X-API-KEY': test_token},
            content_type='application/json'
        )
        assert response.status_code == 401

        data = json.loads(response.data)
        assert 'Max calls' in data['message']
