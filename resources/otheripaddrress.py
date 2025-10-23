"""
Remote IP address lookup API resource.
Provides geolocation data for any given IP address.
"""
from flask_restplus import Resource, fields, Namespace
import netaddr
from flask import request
import logging
from database.country import country_data, get_country_code
from decorators.token import token_required

# Create namespace for API organization
ns_remote = Namespace('whoip', description='IP geolocation operations')

logger_visits = logging.getLogger("logger_visits")

# Define response model for Swagger documentation
schema_fields = ns_remote.model('WHOIP', {
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


class RemoteAddress(Resource):
    """
    Remote IP address lookup resource.

    Provides geolocation and country information for any IP address.
    """

    @ns_remote.response(200, 'Success', schema_fields)
    @ns_remote.response(400, 'Invalid IP address')
    @ns_remote.response(401, 'Unauthorized - Invalid or missing API key')
    @ns_remote.doc(description='Get geolocation data for any IP address')
    @ns_remote.doc(security='apikey')
    @ns_remote.doc(params={'ipaddress': 'IPv4 or IPv6 address to lookup'})
    # Uncomment to require API key authentication:
    # @token_required
    def get(self, ipaddress):
        """
        Lookup geolocation information for a given IP address.

        Args:
            ipaddress: IPv4 or IPv6 address string

        Returns:
            JSON with country, language, currency, and other metadata
        """
        # Validate IP address format
        try:
            netaddr.IPAddress(ipaddress)
        except (netaddr.AddrFormatError, ValueError) as e:
            logger_visits.warning(f"Invalid IP address format: {ipaddress}")
            return {
                'error': 'Invalid IP address',
                'message': 'Please provide a valid IPv4 or IPv6 address',
                'example': '8.8.8.8'
            }, 400

        # Get country code from external API
        country_code = get_country_code(ipaddress)

        # Get country metadata from CSV database
        country_info = country_data(country_code)

        # Build response
        result = {
            'ip': ipaddress,
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
        requester_addr = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
        requester_referrer = request.headers.get('User-Agent', 'Unknown')
        logger_visits.info(
            f"IP lookup from {requester_addr} ({requester_referrer}): "
            f"{ipaddress} -> {country_info.get('Name', 'Unknown')}"
        )

        return result, 200


# Register resource with namespace
ns_remote.add_resource(RemoteAddress, '/remip/<string:ipaddress>')