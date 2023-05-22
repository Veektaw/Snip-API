from flask_restx import Namespace , Resource , fields
from ..utility import db
from ..helpers.mail_sender import MailService, TokenService
from http import HTTPStatus
from flask import request , Response
from api.models.user import User
from .serializer import (manage_namespace,
                         password_change,
                         password_reset_confirm,
                         password_reset_mail,
                         user_serializer)
from flask_jwt_extended import get_jwt_identity, jwt_required 
from threading import Thread
from werkzeug.security import generate_password_hash , check_password_hash



@manage_namespace.route('/password-reset')
class ResetPasswordRequest(Resource):
 
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
                           'public_id':public_id}).start()
            
        response = {
        "success":True,
        "detail":'Instruction to reset your password has been sent to the provided email' 
        }
        return  response , HTTPStatus.OK



@manage_namespace.route('/password-change')
class ChangePasswordRequest(Resource):
 
    @manage_namespace.expect(password_change)
    @manage_namespace.doc(description='Change user password')
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
                if user and check_password_hash(user.password_hash , old_password):
                    
                    user.password_hash = generate_password_hash(confirm_password)
                    user.save()
                    response = {"success":True,
                                "detail":"Password updated successfully"
                                }
                    
                    return response , HTTPStatus.OK
                
                response = {'success': False , 'detail':'Current password is not correct'}
                return response , HTTPStatus.BAD_REQUEST
        response = {'success': False , 'detail':'Passwords does not match'}
        return response , HTTPStatus.BAD_REQUEST



@manage_namespace.route('/password-reset/<token>/<public_id>/confirm')
class ResetPasswordRequestConfirm(Resource):

    @manage_namespace.expect(password_reset_confirm) 
    @manage_namespace.doc(description='Request a password reset mail')
     
    def post(self, token, public_id):
        
        data = request.get_json()
        
        password1 = data.get('password1', None)
        password2 = data.get('password2', None)
         
        if password1 and password2:
            if password1 == password2:
                
                if TokenService.validate_password_reset_token(token, public_id ):
                    
                    user = User.query.filter_by(uuid=public_id).first()
                    
                    if user:
                        user.password_hash = generate_password_hash(password2)
                        user.save()
                        
                        response = {'success':True, 'detail':'Password updated successfully'}
                        
                        return response , HTTPStatus.OK
                    
                response = {'success': False , 'detail':'Password reset link is invalid'}
                
                return response , HTTPStatus.BAD_REQUEST
            
        response = {'success': False , 'detail':'Passwords does not match'}
        
        return response , HTTPStatus.BAD_REQUEST