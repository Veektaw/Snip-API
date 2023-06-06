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
        
        
    def test_signup(self):
        
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
        
        
    def test_login(self):
    
        user = User (
            first_name="Test",
            last_name="User",
            email="testuser@example.com",
            password=generate_password_hash("password")
        )
        db.session.add(user)
        db.session.commit()

        data = {
            "email": "testuser@example.com",
            "password": "password"
        }
        response = self.client.post('/auth/login', json=data)

        assert response.status_code == HTTPStatus.CREATED
        assert "access_token" in response.json
        assert "refresh_token" in response.json
        

    # def test_login_with_invalid_credentials(self):
        
    #     payload = {
    #         'email': 'testuser@gmail.com',
    #         'password': 'wrongpassword'
    #     }

    #     response = self.client.post('/auth/login', json=payload)

    #     self.assertEqual(response.status_code, 404)
    #     self.assertIn('message', response.json)
    #     self.assertEqual(response.json['message'], 'Invalid credentials')
        
        
    # def test_user_logout(self):

    #     token = create_access_token(identity='testuser')
    #     headers = {
    #         "Authorization": f"Bearer {token}"
    #     }

    #     response = self.client.post('/auth/logout', headers=headers)

    #     self.assertEqual(response.status_code, 200)
    #     data = response.get_json()
    #     self.assertEqual(data['message'], 'Successfully logged out')
        
    