from flask import Flask, jsonify, request
from flask_caching import Cache
from flask_admin import Admin
from functools import wraps
from flask_restx import Api
from .auth.views import auth_namespace
from .urls.views import url_namespace
from .urls.admin import UserView
from .visitor.views import visitor_namespace
from .account_management.views import manage_namespace
from .config.config import config_dict
from .utility import db, cache, limiter, redis_cache, jwt, admin, blocklist
from redis import Redis
from flask_caching.backends import RedisCache
from .models.url import Url
from .models.user import User, Token
from .models.tokenblocklist import TokenBlocklist
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
    
    
    jwt = JWTManager(app)
    bcrypt = Bcrypt(app)
    migrate = Migrate(app, db)
    
    admin = Admin(app)
    admin.add_view(UserView(User, db.session))
    admin.add_view(UserView(Token, db.session))
    admin.add_view(UserView(Url, db.session))
    
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

    
    redis_client = Redis.from_url(app.config['RATELIMIT_STORAGE_URL'])
    limiter = Limiter(app, storage_uri=redis_client)
    
    redis_cache = RedisCache(app)
    cache.init_app(app, config={'CACHE_TYPE': 'flask_caching.backends.RedisCache'})
    
    api.add_namespace(url_namespace, path='/url')
    api.add_namespace(visitor_namespace, path='/visitor')
    api.add_namespace(manage_namespace, path='/manage')
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
            'user': User,
            'Token': Token,
            'TokenBlocklist': TokenBlocklist,
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
    
    
    @jwt.token_in_blocklist_loader
    def check_if_token_in_blocklist(jwt_header, jwt_payload):
        return jwt_payload["jti"] in blocklist


    @jwt.revoked_token_loader
    def revoked_token_callback(jwt_header, jwt_payload):
        return (
            jsonify(
                {"description": "The token has been revoked.", "error": "token_revoked"}
            ),
            401,
        )
    

    return app