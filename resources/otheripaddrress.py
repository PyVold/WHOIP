from email.policy import default
from flask_restplus import Resource, fields, marshal_with, Namespace
# netaddr is a fast easy python library to make IP address related operations, but we can get rid of it and make it
# from scratch like: sum(bin(int(x)).count('1') for x in ,mask.split('.'))
import netaddr
from marshmallow import Schema
from flask import request, jsonify, Blueprint
import logging
from logbase import call_logger, setup_logger
from database.country import country_data as cdata
from database.country import get_country_code
from decorators.token import token_required

ns_remote = Namespace('whoip')

logger_visits = logging.getLogger("logger_visits")

schema_fields = ns_remote.model('WHOIP', {
    'ip': fields.String(required=True, default="0.0.0.0"),
    'country': fields.String(required=True, default="EG"),
    'languages': fields.List(fields.String(), required=False, default=['en', 'ar']),
    'currency': fields.String(required=False, default="EGP"),
    'code': fields.String(required=False, default="NA"),
    'native': fields.String(required=False, default="العربية"),
    'phone_code': fields.String(required=False, default="+20"),
    'continent': fields.String(required=False, default="Afriqa"),
    'capital': fields.String(required=False, default="Cairo")
})

class RemoteAddress(Resource):
    @ns_remote.marshal_with(schema_fields, mask=None)
    @ns_remote.doc(responses={200: "success", 400: 'Invalid Argument', 401: 'Invalid token'})
    #@ns_remote.expect(resource_fields)
    #@ns_remote.doc(params={'user': 'username'})
    @ns_remote.doc(description='Remote IP address WHOIS')
    @ns_remote.doc(security='apikey')
    @token_required
    def get(self, ipaddress, mask=None):
        try:
            netaddr.IPAddress(ipaddress)
        except:
            return {'message': 'Invalid IP address'}, 400
        result = {}        
        result['ip'] = ipaddress
        country_code = get_country_code(ipaddress)
        country_data = cdata(country_code)
        result['country'] = country_data['Name']
        result['languages'] = country_data['Languages'].split(',')
        result['currency'] = country_data['Currency']
        result['phone_code'] = "+" + country_data['Phone']
        result['native'] = country_data['Native']
        result['continent'] = country_data['Continent']
        result['capital'] = country_data['Capital']
        result['code'] = country_code
        requester_addr = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
        requester_referrer = request.headers.get('User-Agent')
        logger_visits.info("{} request for Remote IP address: {}, Country: {}".format(requester_referrer,ipaddress, country_data['Name']))
        return result, 200

ns_remote.add_resource(RemoteAddress, '/remip/<string:ipaddress>')