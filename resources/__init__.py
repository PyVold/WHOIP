from flask_restplus import Api
from .myipaddress import ns_myip
from .otheripaddrress import ns_remote
from flask import Blueprint

blueprint = Blueprint('api', __name__, url_prefix='/api')


authorizations = {
    'apikey': {
        'type': 'apiKey',
        'in': 'header',
        'name': 'X-API-KEY'
    }
}

api = Api(blueprint,
    title='IPDevOps Whois',
    version='2.0',
    description='The best whois service',
    authorizations=authorizations
)


api.add_namespace(ns_myip)
api.add_namespace(ns_remote)
