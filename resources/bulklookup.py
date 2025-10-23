"""
Bulk IP address lookup API resource.
Allows looking up multiple IP addresses in a single request.
"""
from flask_restplus import Resource, fields, Namespace
from flask import request
import logging
import netaddr
from database.country import country_data, get_country_code
from decorators.token import token_required

# Create namespace for API organization
ns_bulk = Namespace('bulk', description='Bulk IP geolocation operations')

logger = logging.getLogger(__name__)

# Define response models
single_result_model = ns_bulk.model('SingleIPResult', {
    'ip': fields.String(required=True, description='IP address', example="8.8.8.8"),
    'country': fields.String(description='Country name', example="United States"),
    'code': fields.String(description='2-letter country code', example="US"),
    'currency': fields.String(description='Currency code', example="USD"),
    'continent': fields.String(description='Continent name', example="North America"),
    'error': fields.String(description='Error message if lookup failed')
})

bulk_request_model = ns_bulk.model('BulkIPRequest', {
    'ips': fields.List(
        fields.String,
        required=True,
        description='List of IP addresses to lookup (max 100)',
        example=["8.8.8.8", "1.1.1.1", "208.67.222.222"]
    )
})

bulk_response_model = ns_bulk.model('BulkIPResponse', {
    'total': fields.Integer(description='Total IPs requested'),
    'successful': fields.Integer(description='Number of successful lookups'),
    'failed': fields.Integer(description='Number of failed lookups'),
    'results': fields.List(fields.Nested(single_result_model))
})


class BulkIPLookup(Resource):
    """
    Bulk IP address lookup resource.

    Allows looking up multiple IP addresses in a single API call.
    Useful for batch processing and reducing API call overhead.
    """

    @ns_bulk.expect(bulk_request_model)
    @ns_bulk.response(200, 'Success', bulk_response_model)
    @ns_bulk.response(400, 'Bad Request - Invalid input')
    @ns_bulk.response(401, 'Unauthorized - Invalid or missing API key')
    @ns_bulk.doc(description='Lookup multiple IP addresses in one request (max 100)')
    @ns_bulk.doc(security='apikey')
    @token_required
    def post(self):
        """
        Perform bulk IP geolocation lookup.

        Accepts a JSON payload with a list of IP addresses and returns
        geolocation data for each one.

        Returns:
            JSON with results array and statistics
        """
        # Get JSON payload
        data = request.get_json()

        if not data or 'ips' not in data:
            return {
                'error': 'Bad Request',
                'message': 'Request body must contain "ips" array',
                'example': {'ips': ['8.8.8.8', '1.1.1.1']}
            }, 400

        ip_list = data['ips']

        # Validate input
        if not isinstance(ip_list, list):
            return {
                'error': 'Bad Request',
                'message': '"ips" must be an array of IP addresses'
            }, 400

        if len(ip_list) == 0:
            return {
                'error': 'Bad Request',
                'message': 'At least one IP address is required'
            }, 400

        if len(ip_list) > 100:
            return {
                'error': 'Bad Request',
                'message': 'Maximum 100 IP addresses allowed per request',
                'received': len(ip_list)
            }, 400

        # Process each IP
        results = []
        successful = 0
        failed = 0

        for ip in ip_list:
            try:
                # Validate IP format
                netaddr.IPAddress(ip)

                # Get country code
                country_code = get_country_code(ip)

                # Get country data
                country_info = country_data(country_code)

                # Build result
                result = {
                    'ip': ip,
                    'code': country_code,
                    'country': country_info.get('Name', 'Unknown'),
                    'native': country_info.get('Native', ''),
                    'languages': country_info.get('Languages', '').split(',') if country_info.get('Languages') else [],
                    'currency': country_info.get('Currency', ''),
                    'phone_code': f"+{country_info.get('Phone', '')}" if country_info.get('Phone') else '',
                    'continent': country_info.get('Continent', ''),
                    'capital': country_info.get('Capital', '')
                }

                results.append(result)
                successful += 1

            except (netaddr.AddrFormatError, ValueError) as e:
                logger.warning(f"Invalid IP address in bulk request: {ip}")
                results.append({
                    'ip': ip,
                    'error': 'Invalid IP address format'
                })
                failed += 1

            except Exception as e:
                logger.error(f"Error processing IP {ip}: {e}")
                results.append({
                    'ip': ip,
                    'error': 'Lookup failed'
                })
                failed += 1

        # Log the request
        requester_addr = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
        logger.info(f"Bulk lookup from {requester_addr}: {len(ip_list)} IPs, {successful} successful, {failed} failed")

        return {
            'total': len(ip_list),
            'successful': successful,
            'failed': failed,
            'results': results
        }, 200


# Register resource
ns_bulk.add_resource(BulkIPLookup, '/lookup')
