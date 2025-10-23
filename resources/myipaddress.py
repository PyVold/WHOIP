"""
Current IP address lookup API resource.
Provides geolocation data for the requesting client's IP address.
"""
from flask_restplus import Resource, fields, Namespace
from flask import request
import logging
from database.country import country_data, get_country_code
from decorators.token import token_required

# Create namespace for API organization
ns_myip = Namespace('whoip', description='IP geolocation operations')

logger_visits = logging.getLogger("logger_visits")

# Define response model for Swagger documentation
schema_fields = ns_myip.model('WHOIP', {
    'ip': fields.String(required=True, description='IP address', example="8.8.8.8"),
    'country': fields.String(required=True, description='Country name', example="United States"),
    'languages': fields.List(fields.String(), description='Spoken languages', example=['en']),
    'currency': fields.String(description='Currency code', example="USD"),
    'code': fields.String(description='2-letter country code', example="US"),
    'native': fields.String(description='Native country name', example="United States"),
    'phone_code': fields.String(description='Phone dialing code', example="+1"),
    'continent': fields.String(description='Continent name', example="North America"),
    'capital': fields.String(description='Capital city', example="Washington")
})


class MYIP(Resource):
    """
    Current IP address lookup resource.

    Automatically detects and returns geolocation data for the requesting client's IP.
    """

    @ns_myip.response(200, 'Success', schema_fields)
    @ns_myip.response(401, 'Unauthorized - Invalid or missing API key')
    @ns_myip.doc(description='Get geolocation data for your current IP address')
    @ns_myip.doc(security='apikey')
    # Uncomment to require API key authentication:
    # @token_required
    def get(self):
        """
        Lookup geolocation information for the requesting client's IP address.

        Returns:
            JSON with country, language, currency, and other metadata
        """
        # Extract IP from headers (respects X-Real-IP from proxy)
        ipaddr = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)

        # Get country code from external API
        country_code = get_country_code(ipaddr)

        # Get country metadata from CSV database
        country_info = country_data(country_code)

        # Build response
        result = {
            'ip': ipaddr,
            'code': country_code,
            'country': country_info.get('Name', 'Unknown'),
            'native': country_info.get('Native', ''),
            'languages': country_info.get('Languages', '').split(',') if country_info.get('Languages') else [],
            'currency': country_info.get('Currency', ''),
            'phone_code': f"+{country_info.get('Phone', '')}" if country_info.get('Phone') else '',
            'continent': country_info.get('Continent', ''),
            'capital': country_info.get('Capital', '')
        }

        # Log the request
        logger_visits.info(f"My IP lookup: {ipaddr} -> {country_info.get('Name', 'Unknown')}")

        return result, 200


# Register resource with namespace
ns_myip.add_resource(MYIP, '/myip/')