import unittest
from .. import create_app
from ..config.config import config_dict
from ..utility import db
from http import HTTPStatus
from werkzeug.security import generate_password_hash
from ..models.user import User
from ..models.url import Url
from flask_jwt_extended import create_access_token
import uuid


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
        
        
    def test_user_create_url(self):

        user = User (
            first_name='Test',
            last_name='Tester',
            email='testuser@gmail.com',
            password='password'
        )
        user.save()       
        token = create_access_token(identity=user.email)
        self.return_value = user.email
        
        generated_uuid = uuid.uuid4()
        
        data = {
            'id': [generated_uuid],
            'user_long_url': 'https://www.example.com'
        }    
        
        response = self.client.post('/url/create', json=data, headers={'Authorization': f'Bearer {token}'})
        assert response.status_code == 201
        
        
    def test_user_custom(self):

        user = User (
            first_name='Test',
            last_name='Tester',
            email='testuser@gmail.com',
            password='password'
        )
        user.save()
        token = create_access_token(identity=user.email)
        self.return_value = user.email
        
        generated_uuid = uuid.uuid4()
        
        data = {
            'id': [generated_uuid],
            'user_long_url': 'https://www.example.com',
            'user_custom': 'test'
        }    
        
        response = self.client.post('/url/custom', json=data, headers={'Authorization': f'Bearer {token}'})
        assert response.status_code == 201
        
        
    def test_user_gets_urls(self):

        user = User (
            first_name='Test',
            last_name='Tester',
            email='testuser@gmail.com',
            password='password'
        )
        user.save()
        token = create_access_token(identity=user.email)  
        
        response = self.client.get('/url/urls', headers={'Authorization': f'Bearer {token}'})
        assert response.status_code == 200
        
        
    def test_user_gets_urls_by_id(self):

        user = User(
            first_name='Test',
            last_name='Tester',
            email='testuser@gmail.com',
            password='password'
        )
        user.save()
        token = create_access_token(identity=user.email)
        
        url_id = str(uuid.uuid4())

        data = Url(
            id=url_id,
            user_long_url='https://www.testsite.com',
            url_creator=user
        )
        data.save()

        url_endpoint = f'/url/{url_id}'
        response = self.client.get(url_endpoint, headers={'Authorization': f'Bearer {token}'})

        assert response.status_code == 200
        assert response.json['user_long_url'] == 'https://www.testsite.com'
        
        
    def test_user_deletes_url_by_id(self):
        user = User(
            first_name='Test',
            last_name='Tester',
            email='testuser@gmail.com',
            password='password'
        )
        user.save()
        token = create_access_token(identity=user.email)
        
        url_id = str(uuid.uuid4())

        data = Url(
            id=url_id,
            user_long_url='https://www.testsite.com',
            url_creator=user
        )
        data.save()

        url_endpoint = f'/url/{url_id}'
        response = self.client.delete(url_endpoint, headers={'Authorization': f'Bearer {token}'})

        assert response.status_code == 200