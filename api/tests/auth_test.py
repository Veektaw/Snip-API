import unittest
from .. import create_app
from ..config.config import config_dict
from ..utility import db
from http import HTTPStatus
from werkzeug.security import generate_password_hash
from ..models.user import User
from flask_jwt_extended import create_access_token


class UserTestCase(unittest.TestCase):
    
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
        
    def test_user_registration(self):

        data = {
            "id": 1,
            "first_name": "Test",
            "last_name": "Tester",
            "email": "testuser@gmail.com",
            "password": "password"
        }

        response = self.client.post('/auth/signup', json=data)
        user = User.query.filter_by(email='testuser@gmail.com').first()
        assert user.email == "testuser@gmail.com"
        assert response.status_code == 201