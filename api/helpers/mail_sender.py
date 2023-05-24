import ssl
import smtplib
import os
import json
import secrets
from email.message import EmailMessage
from datetime import datetime  
from functools import wraps
from flask import redirect , url_for, Request
from googleapiclient.errors import HttpError 
from ..utility import db
from api.models.user import User, Token
import base64
from email.mime.text import MIMEText
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from requests import HTTPError


secrets.token_hex()


SCOPES = ["https://www.googleapis.com/auth/gmail.send"]


flow = InstalledAppFlow.from_client_secrets_file('credentials/credentials.json', SCOPES)
credentials = flow.run_local_server(port=0)

service = build('gmail', 'v1', credentials=credentials)

class MailService:

    def send_reset_mail(*args, **kwargs):
        
        """
        Send password reset token to the email address in the kwargs
        
        """
        
        token = kwargs['token']
        public_id = kwargs['public_id']
        
        message = MIMEText(f'You are receiving this email because you have requested for a new password.\nYou can ignore if you did not make this request.\nClick the link below to set a new password.\nhttp://127.0.0.1:5000/password-reset/{token}/{public_id}/confirm')
        
        message['to'] = kwargs['email']
        message['subject'] = 'Password Reset'

        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
        create_message = {'raw': raw_message}

        try:
            response = service.users().messages().send(userId='me', body=create_message).execute()
            print(f'Successfully sent email to {kwargs["email"]}. Message ID: {response["id"]}')
        except HttpError as error:
            print(f'An error occurred while sending the email to: {error}')


class TokenService:

    def create_password_reset_token(user_id:str )-> str :
        """
        Generate a token for a user.
        :param user_id: The id of a user

        """
        reset_token = secrets.token_hex(20) + secrets.token_urlsafe(20)
        token = Token(user_id=user_id, token=reset_token)
        
        try:
           token.save()
           
        except:
            db.session.rollback()
            return None
        
        return reset_token


    def validate_password_reset_token(token:str , user_public_id):
        
        try:
            user = User.query.filter_by(public_id=user_public_id).first()
            
        except Exception as e :
            return False
        
        token_object = Token.query.filter_by(user=user.id, token=token, password=True).first()
        
        if token_object:
            current_time = datetime.now()
            time_diff_timedelta = current_time - token_object.created_at 
            hours = time_diff_timedelta.seconds > 3600
            
            if hours > 1 : 
                token_object.delete()
                return False
            
            token_object.delete()
            return True
        
        return False