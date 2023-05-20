from flask import Flask, jsonify
from flask_caching import Cache
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
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_cors import CORS
from flask_bcrypt import Bcrypt
import logging
from logging.handlers import RotatingFileHandler

cache = Cache()

def create_app(config=config_dict['dev']):
    app = Flask(__name__)
    app.config.from_object(config)
    CORS(app)
    
    #cache = Cache(app, config={'CACHE_TYPE': 'simple', 'CACHE_DEFAULT_TIMEOUT': 300})
    
    
    
    log_file = 'app.log'
    log_formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    log_handler = RotatingFileHandler(log_file, maxBytes=1024 * 1024, backupCount=10)
    log_handler.setFormatter(log_formatter)

    cache = Cache(app, config={'CACHE_TYPE': 'simple', 'CACHE_DEFAULT_TIMEOUT': 300})
    cache.init_app(app)

    logger = logging.getLogger('my_logger')
    logger.addHandler(log_handler)
    logger.setLevel(logging.INFO)
    
    
    class FlaskCacheHandler(logging.Handler):
        def emit(self, record):
            cache_key = 'log_cache_key'
            logs = cache.get(cache_key) or []
            logs.append(self.format(record))
            cache.set(cache_key, logs)

    flask_cache_handler = FlaskCacheHandler()
    logger.addHandler(flask_cache_handler) 
    
    #limiter = Limiter(app, key_func=get_remote_address)

    db.init_app(app)

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