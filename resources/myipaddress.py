from typing import Literal
from flask_restplus import Resource, fields, Namespace, marshal_with
from marshmallow import Schema 
from flask import request, jsonify, make_response, request, Blueprint
import logging
from logbase import call_logger, setup_logger
from database.country import country_data as cdata
from database.country import get_country_code
from decorators.token import token_required


ns_myip = Namespace('whoip', description='WHOIS IP Address')

logger_visits = logging.getLogger("logger_visits")

schema_fields = ns_myip.model('WHOIP', {
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

class MYIP(Resource):
    #@ns_myip.marshal_with(schema_fields, mask=None)
    @ns_myip.response(model=schema_fields, code=200, description='success')
    @ns_myip.doc(description='My IP address WHOIS')
    @ns_myip.doc(security='apikey')
    #@token_required
    def get(self):
        result = {}
        ipaddr = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
        result['ip'] = ipaddr
        country_code = get_country_code(ipaddr)
        country_data = cdata(country_code)
        result['languages'] = country_data['Languages'].split(',')
        result['currency'] = country_data['Currency']
        result['country'] = country_data['Name']
        result['phone_code'] = "+" + country_data['Phone']
        result['native'] = country_data['Native']
        result['continent'] = country_data['Continent']
        result['capital'] = country_data['Capital']
        result['code'] = country_code
        logger_visits.info("IP address: {}, Country: {}".format(ipaddr, country_data['Name']))
        return result, 200

ns_myip.add_resource(MYIP, '/myip/')