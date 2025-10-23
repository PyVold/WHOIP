# WHOIP - IP Geolocation & WHOIS Service

> A comprehensive IP geolocation API providing country, language, currency, and geographic metadata for any IP address.

[![Python](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Flask](https://img.shields.io/badge/flask-1.1.4-green.svg)](https://flask.palletsprojects.com/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

## Features

- **IP Geolocation**: Lookup geographic and country data for any IPv4/IPv6 address
- **My IP Lookup**: Automatically detect and geolocate the requester's IP
- **Bulk Lookup**: Process up to 100 IP addresses in a single request
- **User Management**: Multi-user system with authentication
- **API Token System**: Secure token-based API authentication
- **Rate Limiting**: Configurable daily rate limits per token
- **Admin Panel**: Flask-Admin dashboard for user and token management
- **Comprehensive Logging**: Organized daily logs for auditing
- **Docker Support**: Production-ready containerization
- **Swagger Documentation**: Interactive API documentation

## Quick Start

### Prerequisites

- Python 3.9+
- pip
- (Optional) Docker & Docker Compose

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/PyVold/WHOIP.git
   cd WHOIP
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env and set SECRET_KEY and other settings
   ```

5. **Initialize database**
   ```bash
   python app.py  # Creates tables on first run
   ```

6. **Run the application**
   ```bash
   # Development
   python app.py

   # Production with Gunicorn
   gunicorn -w 4 -b 0.0.0.0:5500 app:app
   ```

7. **Access the application**
   - API Documentation: http://localhost:5500/api/
   - User Dashboard: http://localhost:5500/myapi/
   - Admin Panel: http://localhost:5500/admin/
   - Health Check: http://localhost:5500/health

### Docker Deployment

```bash
# Build and run with Docker Compose
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## API Endpoints

### Public Endpoints (No Authentication Required)

#### Get My IP Information
```bash
GET /api/whoip/myip/
```

**Example:**
```bash
curl http://localhost:5500/api/whoip/myip/
```

**Response:**
```json
{
  "ip": "8.8.8.8",
  "code": "US",
  "country": "United States",
  "native": "United States",
  "languages": ["en"],
  "currency": "USD",
  "phone_code": "+1",
  "continent": "North America",
  "capital": "Washington"
}
```

#### Get Remote IP Information
```bash
GET /api/whoip/remip/<ipaddress>
```

**Example:**
```bash
curl http://localhost:5500/api/whoip/remip/1.1.1.1
```

### Protected Endpoints (Require API Token)

#### Bulk IP Lookup
```bash
POST /api/bulk/lookup
Headers: X-API-KEY: <your-token>
Content-Type: application/json
```

**Example:**
```bash
curl -X POST http://localhost:5500/api/bulk/lookup \
  -H "X-API-KEY: your-token-here" \
  -H "Content-Type: application/json" \
  -d '{
    "ips": ["8.8.8.8", "1.1.1.1", "208.67.222.222"]
  }'
```

**Response:**
```json
{
  "total": 3,
  "successful": 3,
  "failed": 0,
  "results": [
    {
      "ip": "8.8.8.8",
      "code": "US",
      "country": "United States",
      ...
    },
    ...
  ]
}
```

## User & Token Management

### 1. Register an Account
Navigate to http://localhost:5500/myapi/signup/ and create an account.

### 2. Login
Login at http://localhost:5500/myapi/login/

### 3. Create API Token
- Go to http://localhost:5500/myapi/tokens/
- Create a new application
- Copy the generated API token
- Wait for admin approval (or approve via admin panel)

### 4. Use API Token
Include the token in API requests:
```bash
curl -H "X-API-KEY: your-token-here" http://localhost:5500/api/bulk/lookup
```

## Configuration

All configuration is managed through environment variables. See `.env.example` for all available options.

### Key Settings

| Variable | Description | Default |
|----------|-------------|---------|
| `SECRET_KEY` | Flask secret key (REQUIRED in production) | Random |
| `DATABASE_URL` | Database connection string | `sqlite:///lite2.db` |
| `MAX_APPS_PER_USER` | Max API tokens per user | `3` |
| `DEFAULT_RATE_LIMIT` | Daily API call limit per token | `1000` |
| `RIPE_API_TIMEOUT` | Timeout for external API calls | `5` |
| `ADMIN_USERS` | Comma-separated list of admin usernames | `admin` |

## Admin Panel

Access the admin panel at http://localhost:5500/admin/

**Default Admin Setup:**
1. Create a user with username matching `ADMIN_USERS` in `.env`
2. Login with that user
3. Access /admin/ to manage users and tokens

**Admin Functions:**
- View/edit all users
- View/edit all API tokens
- Approve token requests
- Adjust rate limits
- Deactivate tokens

## Architecture

```
WHOIP/
├── app.py                 # Main Flask application
├── config.py              # Configuration management
├── utils.py               # Utility functions (validation)
├── logbase.py             # Logging configuration
├── access/                # Authentication & user management
│   ├── __init__.py        # User & Application models
│   ├── login.py           # Login & token management
│   ├── signup.py          # User registration
│   ├── delete.py          # Token deletion
│   └── templates/         # HTML templates
├── resources/             # API endpoints
│   ├── __init__.py        # API initialization
│   ├── myipaddress.py     # /myip endpoint
│   ├── otheripaddrress.py # /remip endpoint
│   └── bulklookup.py      # /bulk endpoint
├── database/              # Data layer
│   ├── country.py         # IP geolocation logic
│   └── data.csv           # Country metadata (251 countries)
├── decorators/            # Custom decorators
│   └── token.py           # Token authentication & rate limiting
└── logs/                  # Application logs (auto-created)
```

## Security Features

- **Secure Password Hashing**: pbkdf2:sha256 with 600,000 iterations
- **Protected Admin Panel**: Admin-only access with authentication
- **Token-Based API Auth**: Secure API key authentication
- **Rate Limiting**: Per-token daily limits with automatic reset
- **Input Validation**: Comprehensive validation for all user inputs
- **SQL Injection Protection**: SQLAlchemy ORM prevents SQL injection
- **CSRF Protection**: Built-in Flask CSRF protection
- **Session Security**: Secure cookie configuration
- **Environment-Based Secrets**: No hardcoded credentials

## Performance Optimizations

- **CSV Caching**: Country data loaded once at startup
- **Request Timeouts**: 5-second timeout for external API calls
- **Database Indexes**: Optimized queries with indexes on username, email, token
- **Connection Pooling**: SQLAlchemy connection pooling
- **Gunicorn Workers**: Multi-process WSGI server for production

## Logging

Logs are organized by date in `logs/<date>/`:
- `uses.log`: General application logs
- `visits.log`: API request logs

## Development

### Running Tests
```bash
# TODO: Add pytest tests
pytest tests/
```

### Code Quality
```bash
# Format code
black .

# Lint
flake8 .

# Type checking
mypy .
```

## Deployment

### Production Checklist

- [ ] Set `FLASK_ENV=production`
- [ ] Set strong `SECRET_KEY` (use `secrets.token_hex(32)`)
- [ ] Use PostgreSQL instead of SQLite
- [ ] Set `SESSION_COOKIE_SECURE=True` (HTTPS only)
- [ ] Configure reverse proxy (Nginx/Apache)
- [ ] Set up SSL/TLS certificates
- [ ] Configure firewall rules
- [ ] Set up monitoring and alerts
- [ ] Configure log rotation
- [ ] Set up automated backups
- [ ] Review and adjust rate limits

### Nginx Configuration Example

```nginx
server {
    listen 80;
    server_name yourdomain.com;

    location / {
        proxy_pass http://127.0.0.1:5500;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_set_header Host $host;
    }
}
```

## Troubleshooting

### Issue: "Token is not recognized"
- Verify token is correct
- Check token status in admin panel (must be "active")
- Ensure token is passed in `X-API-KEY` header

### Issue: "Max calls reached"
- Rate limit exceeded for the day
- Resets at midnight UTC
- Contact admin to increase limit

### Issue: Database errors on startup
- Delete `lite2.db` and restart
- Database will be recreated automatically

### Issue: External API timeouts
- Increase `RIPE_API_TIMEOUT` in `.env`
- Check network connectivity

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

- **Issues**: [GitHub Issues](https://github.com/PyVold/WHOIP/issues)
- **Documentation**: [API Docs](http://localhost:5500/api/)
- **Email**: support@ipdevops.com

## Roadmap

- [ ] Redis caching for IP lookups
- [ ] WebSocket real-time API
- [ ] ASN and ISP information
- [ ] Threat intelligence integration
- [ ] Email verification for signup
- [ ] Password reset functionality
- [ ] Two-factor authentication
- [ ] User analytics dashboard
- [ ] API usage statistics
- [ ] Subscription tiers
- [ ] Client SDKs (Python, Node.js, Go)
- [ ] Mobile app (iOS/Android)

## Acknowledgments

- [RIPE NCC](https://www.ripe.net/) for MaxMind GeoLite API
- [Flask](https://flask.palletsprojects.com/) web framework
- [MaxMind](https://www.maxmind.com/) for geolocation data

---

**Made with ❤️ by IPDevOps Team**
