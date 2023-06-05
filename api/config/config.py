import os
from flask_caching import Cache
from decouple import config
from datetime import timedelta

BASE_DIR = os.path.dirname(os.path.realpath(__file__))

db_name = 'scissor_db'

#default_uri = "postgres://{}:{}@{}/{}".format('postgres', 'password', 'localhost:5432', db_name)



class Config:
    SECRET_KEY = config('SECRET_KEY', 'secret')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=59)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(minutes=59)
    JWT_SECRET_KEY = config('JWT_SECRET_KEY')
    CACHE_TYPE = 'redis'
    CACHE_DEFAULT_TIMEOUT = 50
    DEFAULT_LIMITS = ["5 per minute"]
    CACHE_REDIS_URL = "redis://localhost:6379"
 
class DevConfig(Config):
    DEBUG = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIR, 'db.sqlite3')
    CACHE_TYPE = 'flask_caching.backends.RedisCache'
    CACHE_REDIS_URL = "redis://localhost:6379"
    CACHE_DEFAULT_TIMEOUT = 50
    DEFAULT_LIMITS = ["5 per minute"]
    RATELIMIT_STORAGE_URL = os.environ.get('REDIS_URL') or 'redis://localhost:6379'

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = True
    SQLALCHEMY_DATABASE_URI = 'sqlite://'
    CACHE_DEFAULT_TIMEOUT = 50
    CACHE_TYPE = 'flask_caching.backends.RedisCache'
    DEFAULT_LIMITS = ["5 per minute"]
    JWT_BLACKLIST_ENABLED = True
    JWT_BLACKLIST_TOKEN_CHECKS = 'access', 'refresh'
    STORAGE_URI = "redis://localhost:6379"
    CACHE_REDIS_URL = "redis://localhost:6379"
    RATELIMIT_STORAGE_URL = os.environ.get('REDIS_URL') or 'redis://localhost:6379'
    
class ProdConfig(Config):
    
    uri = os.environ.get('DATABASE_URL') # or other relevant config var
    if uri and uri.startswith('postgres://'):
        uri = uri.replace('postgres://', 'postgresql://', 1)
    
    SQLALCHEMY_DATABASE_URI = uri
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG = config('DEBUG', False, cast=bool)
    SECRET_KEY = config('SECRET_KEY', 'secret')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=59)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(minutes=59)
    JWT_SECRET_KEY = config('JWT_SECRET_KEY')
    CACHE_TYPE = 'flask_caching.backends.RedisCache'
    CACHE_REDIS_URL = "redis://localhost:6379"
    CACHE_DEFAULT_TIMEOUT = 50
    DEFAULT_LIMITS = ["5 per minute"]
    RATELIMIT_STORAGE_URL = os.environ.get('REDIS_URL') or 'redis://localhost:5000'


config_dict = {
    'dev' : DevConfig,
    'prod' : ProdConfig,
    'test': TestConfig
}