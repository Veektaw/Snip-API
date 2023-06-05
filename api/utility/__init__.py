from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_caching import Cache
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_caching.backends import RedisCache
from flask_jwt_extended import JWTManager
from flask_admin import Admin


db = SQLAlchemy()
bcrypt = Bcrypt()
cache = Cache()
redis_cache = RedisCache()
limiter = Limiter(key_func=get_remote_address)
blocklist = set()
jwt = JWTManager()
admin = Admin()