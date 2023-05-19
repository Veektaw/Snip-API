from flask import Flask, jsonify
from functools import wraps
from flask_restx import Api
from .auth.views import auth_namespace
from .urls.views import url_namespace
from .config.config import config_dict
from .utility import db
from .models.url import Url
from .models.user import User
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager, verify_jwt_in_request, get_jwt, create_access_token
from werkzeug.exceptions import NotFound, NotAcceptable, MethodNotAllowed

def create_app(config=config_dict['dev']):
    app = Flask(__name__)


    app.config.from_object(config)

    db.init_app(app)

    jwt = JWTManager(app)

    migrate = Migrate(app, db)

    authorizations = {
        'Bearer Auth':{
           "type": "apiKey",
           "in": "Header",
           "name": "Authorization",
           "description": "Add a JWT token to the header with ** Bearer <JWT Token>" 
        }
    }

    api = Api(app, title='Stdent portal API',
              description='A student portal API',
              version = 1.0,
              authorizations=authorizations,
              security='Bearer Auth')

    
    api.add_namespace(url_namespace, path='/url')
    api.add_namespace(auth_namespace, path='/auth')

    @api.errorhandler(NotFound)
    def not_found(error):
        return {"error": "Not found"}, 404
    
    @api.errorhandler(MethodNotAllowed)
    def method_not_allowed(error):
        return {"error": "Method not allowed"}, 404

    @app.shell_context_processor
    def make_shell_context():
        return {
            'db': db,
            'url': Url,
            'user': User
        }

    return app