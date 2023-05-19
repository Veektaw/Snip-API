from flask import request
import random, string
from flask_restx import Namespace, Resource, fields
from ..models.user import User
from werkzeug.security import generate_password_hash, check_password_hash
from http import HTTPStatus
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from .serializer import signup_expect_model, signup_model, auth_namespace, login_expect_model


@auth_namespace.route('/signup')
class SignUp(Resource):
   
   @auth_namespace.expect(signup_expect_model)
   @auth_namespace.marshal_with(signup_model)
   @auth_namespace.doc(description="Signup user")
   def post(self):
     
      data = request.get_json()

      new_user = User(
         first_name = data.get('first_name'),
         last_name = data.get('last_name'),
         email = data.get('email'),
         password = generate_password_hash(data.get('password'))
      )

      new_user.save()

      return new_user, HTTPStatus.CREATED
  
  
@auth_namespace.route('/login')
class Login(Resource):
   
   @auth_namespace.expect(login_expect_model)
   @auth_namespace.doc(description = "Login user")
   def post(self):
     
      data = request.get_json()

      email = data.get("email")
      password = data.get("password")

      user = User.query.filter_by(email=email).first()

      if (user is not None) and check_password_hash(user.password, password):
         access_token = create_access_token(identity=user.email)
         refresh_token = create_refresh_token(identity=user.email)

         response = {
            'access_token': access_token,
            'refresh_token': refresh_token
         }

         return response, HTTPStatus.CREATED
     
@auth_namespace.route('/refresh')
class Refresh(Resource):

   @auth_namespace.doc(description = "Refresh access token of user login")
   @jwt_required(refresh=True)
   def post(self):
      email = get_jwt_identity()

      access_token = create_access_token(identity=email)

      return {"access_token": access_token}, HTTPStatus.OK