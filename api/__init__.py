from flask import Flask, jsonify, request
from flask_caching import Cache
from functools import wraps
from flask_restx import Api
from .auth.views import auth_namespace
from .urls.views import url_namespace
from .config.config import config_dict
from .utility import db, cache, limiter
from .models.url import Url
from .models.user import User
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager, verify_jwt_in_request, get_jwt, create_access_token
from werkzeug.exceptions import NotFound, NotAcceptable, MethodNotAllowed
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_cors import CORS
from flask_bcrypt import Bcrypt
import logging
from logging.handlers import RotatingFileHandler


def create_app(config=config_dict['dev']):
    app = Flask(__name__)
    app.config.from_object(config)
    CORS(app)

    db.init_app(app)
    
    cache.init_app(app)
    
    jwt = JWTManager(app)
    bcrypt = Bcrypt(app)
    migrate = Migrate(app, db)
    
    authorizations = {
        'Bearer Auth':{
           "type": "apiKey",
           "in": "Header",
           "name": "Authorization",
           "description": "Add a JWT token to the header with ** Bearer <JWT Token>" 
        }
    }

    api = Api(app, title='Scissor',
              description='A URL shortening API',
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

    log_file = 'app.log'
    log_formatter = logging.Formatter('%(asctime)s %(levelname)s: %(remote_addr)s - %(message)s',
                                      datefmt='%Y-%m-%d %H:%M:%S')

    class ClientIPFilter(logging.Filter):
        def filter(self, record):
            record.remote_addr = request.remote_addr
            record.method = request.method
            record.url = request.url
            return True

    log_handler = RotatingFileHandler(log_file, maxBytes=1024 * 1024, backupCount=10)
    log_handler.setFormatter(log_formatter)
    log_handler.addFilter(ClientIPFilter())
    app.logger.addHandler(log_handler)
    

    return app