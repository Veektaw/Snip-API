from flask_restx import Namespace , Resource , fields
from ..utility import db
from ..helpers.mail_sender import MailService, TokenService
from http import HTTPStatus
from flask import request , Response
from api.models.user import User, Token
from .serializer import (manage_namespace,
                         password_change,
                         password_reset_confirm,
                         password_reset_mail,
                         user_serializer)
from flask_jwt_extended import get_jwt_identity, jwt_required 
from threading import Thread
from werkzeug.security import generate_password_hash , check_password_hash



@manage_namespace.route('/password-reset')
class ResetPassword(Resource):
 
    @manage_namespace.expect(password_reset_mail)
    @manage_namespace.doc(description="Request a password reset mail")
    def post(self):
        
        data = request.get_json()
        email = data.get('email')
        
        user = User.query.filter_by(email=email).first()
        
        if user:
            token = TokenService.create_password_reset_token(user.id)
            public_id = user.id
            
            Thread(target = MailService.send_reset_mail,
                   kwargs={'email': user.email,
                           'token': token,
                           'public_id': public_id}).start()
            
        response = {
        "success":True,
        "detail":'Instruction to reset your password has been sent to the provided email' 
        }
        return  response , HTTPStatus.OK


@manage_namespace.route('/password-reset/<token>/<user_id>/confirm')
class ResetPasswordConfirm(Resource):

    @manage_namespace.expect(password_reset_confirm) 
    @manage_namespace.doc(description="Request a password reset mail")
     
    def post(self, token, user_id):
        data = request.get_json()
        new_password = data.get('new_password')
        confirm_password = data.get('confirm_password')
         
        if new_password and confirm_password:
            
            if new_password == confirm_password:
                
                if TokenService.validate_password_reset_token(token, user_id=user_id):
                    user = User.query.get(user_id)
                    
                    if user:
                        user.password = generate_password_hash(confirm_password)
                        user.save()
                        
                        response = {
                            "success": True,
                            "message": "Password updated successfully"
                        }
                        
                        return response, HTTPStatus.OK
                    
                response = {
                    "success": False,
                    "message": "Password reset link is invalid"
                }
                
                return response, HTTPStatus.BAD_REQUEST
            
        response = {
            "success": False,
            "message": "Passwords do not match"
        }
        
        return response, HTTPStatus.BAD_REQUEST


    
    
@manage_namespace.route('/password-change')
class ChangePasswordRequest(Resource):
 
    @manage_namespace.expect(password_change)
    @manage_namespace.doc(description = "Change user password")
    @jwt_required(False)
    
    def post(self):
        
        user_email = get_jwt_identity()
        
        user = User.query.filter_by(email=user_email).first()
        
        data = request.get_json()
        
        old_password = data.get('old_password', None)
        new_password = data.get('new_password', None)
        confirm_password = data.get('confirm_password' , None)
         
        if new_password and confirm_password :
            if new_password == confirm_password :
                if user and check_password_hash(user.password, old_password):
                    
                    user.password = generate_password_hash(confirm_password)
                    user.save()
                    response = {"success":True,
                                "message":"Password updated successfully"
                                }
                    
                    return response , HTTPStatus.OK
                
                response = {"success": False,
                            "message":"Current password is not correct"}
                
                return response , HTTPStatus.BAD_REQUEST
            
        response = {"success": False,
                    "message":"Passwords does not match"}
        
        return response , HTTPStatus.BAD_REQUEST