"""
API initialization and namespace registration.
Configures Flask-RESTPlus API with all endpoint namespaces.
"""
from flask_restplus import Api
from .myipaddress import ns_myip
from .otheripaddrress import ns_remote
from .bulklookup import ns_bulk
from flask import Blueprint

# Create API blueprint
blueprint = Blueprint('api', __name__, url_prefix='/api')

# Define API authorization schemes
authorizations = {
    'apikey': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'X-API-KEY',
        'description': 'API token obtained from /myapi/tokens dashboard'
    }
}

# Initialize Flask-RESTPlus API
api = Api(
    blueprint,
    title='WHOIP - IP Geolocation API',
    version='2.0',
    description='''
    IP Geolocation and WHOIS Service

    A comprehensive IP geolocation API providing country, language, currency, and other metadata for any IP address.

    ## Features
    - My IP Lookup: Automatically detect and geolocate your current IP
    - Remote IP Lookup: Lookup any IPv4 or IPv6 address
    - Bulk Lookup: Process up to 100 IPs in a single request
    - Rate Limited: Daily limits per API token (default: 1000 calls/day)

    ## Authentication
    Most endpoints require an API key. Get your token at /myapi/tokens

    ## Rate Limiting
    - Free tier: 1,000 requests per day
    - Rate limits reset at midnight UTC
    - Exceeding limits returns HTTP 401
    ''',
    authorizations=authorizations,
    doc='/docs'  # Custom docs endpoint
)

# Register namespaces
api.add_namespace(ns_myip, path='/whoip')
api.add_namespace(ns_remote, path='/whoip')
api.add_namespace(ns_bulk, path='/bulk')
