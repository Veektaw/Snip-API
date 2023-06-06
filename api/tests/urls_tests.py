import unittest
from .. import create_app
from ..config.config import config_dict
from ..utility import db
from http import HTTPStatus
from werkzeug.security import generate_password_hash
from ..models.user import User
from ..models.url import Url
from flask_jwt_extended import create_access_token


class UrlTestCase(unittest.TestCase):
    
    def setUp(self):

        self.app = create_app(config=config_dict['test'])
        self.appctx = self.app.app_context()
        self.appctx.push()
        self.client = self.app.test_client()

        db.create_all()


    def tearDown(self):

        db.drop_all()
        self.appctx.pop()
        self.app = None
        self.client = None
        
        
    def user_creates_short_url(self):

        user = User(
            email='testuser@gmail.com',
            password='password'
        )

        # Login the user to get the access token
        response = self.app.post('/auth/login', json={
            'email': 'testuser@gmail.com',
            'password': 'password'
        })
        
        self.assertEqual(response.status_code, 200)
        access_token = response.json['access_token']

        # Make a request to the create URL endpoint
        headers = {'Authorization': f'Bearer {access_token}'}
        response = self.app.post('/url/create', json={
            'user_long_url': 'https://www.example.com'
        }, headers=headers)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('user_long_url', response.json)
        self.assertIn('short_url', response.json)
        self.assertIn('url_title', response.json)
        self.assertIn('creator', response.json)