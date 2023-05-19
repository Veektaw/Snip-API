import qrcode
import io
from http import HTTPStatus
from flask_restx import Namespace , Resource 
from flask import request , Response, send_file
from flask_jwt_extended import jwt_required , get_jwt_identity
from .serializer import url_expect_serializer , url_marshall_serializer, url_namespace
from ..utility import db
from api.helpers.url_validator import URLCreator
from api.models.user import User
from api.models.url import Url
#from api.auth.views import DateTimeEncoder
 


@url_namespace.route('/create')
class CreateURL(Resource):
   
   @url_namespace.expect(url_expect_serializer)     
   @url_namespace.marshal_with(url_marshall_serializer)
   @url_namespace.doc(description = "Make a url short")   
   @jwt_required()
     
   def post(self):
        
    current_user = get_jwt_identity() 
    authenticated_user = User.query.filter_by(email=current_user).first()  
       
    if not authenticated_user:
        return {"message": "User not found"}, HTTPStatus.NOT_FOUND      
       
    data = request.get_json()
    user_long_url = data.get('user_long_url')
      
    if URLCreator.is_valid_url(user_long_url):
        url_title = URLCreator.extract_url_data(user_long_url)
        short_url = URLCreator.short_url()
         
        url = Url (
            user_long_url = user_long_url,
            short_url = short_url,
            url_title = url_title,
            creator = authenticated_user.email
        )
         
        try:
            url.save()
            
        except:
            db.session.rollback()
            response = {"message": "Error loading"} 
            return response , HTTPStatus.INTERNAL_SERVER_ERROR 
        
        return url, HTTPStatus.OK  
    
    response = {"message": "This is not a valid URL"}
    return response, HTTPStatus.BAD_REQUEST  
   


@url_namespace.route('/urls') 
class GetURLS(Resource):
   
    @url_namespace.doc(description = "Get all urls") 
    @url_namespace.marshal_with(url_marshall_serializer)   
    @jwt_required()
      
    def get(self):
        
        authenticated_user_email = get_jwt_identity() 

        authenticated_user = User.query.filter_by(email = authenticated_user_email).first()
          
        if not authenticated_user:
            return {"message": "User not found"}, HTTPStatus.NOT_FOUND
        
        url = Url.query.filter_by(creator = authenticated_user.email).all()
          
        return url , HTTPStatus.OK
    
    
@url_namespace.route('/<url_uuid>/url')
class GenerateURLQrCodeApiView(Resource):
   
    @url_namespace.doc(description = "Get Analytics")
    @url_namespace.marshal_with(url_marshall_serializer)  
    @jwt_required()
       
    def get(self, url_uuid ):
        authenticated_user_email = get_jwt_identity() 
      
        authenticated_user = User.query.filter_by(email = authenticated_user_email).first()
           
        if not authenticated_user:
            return {"message": "User not found"}, HTTPStatus.NOT_FOUND
        
        url = Url.get_by_id(url_uuid)
        
        return url



@url_namespace.route('/info') 
class GetURLSBreakDownApiView(Resource):
   
    @url_namespace.doc(description= "Get infomation about urls")    
    @jwt_required()
    
    def get(self):
        authenticated_user_email = get_jwt_identity() 
        authenticated_user = User.query.filter_by(email = authenticated_user_email).first()
           
        if not authenticated_user:
            return {"message": "User does not exist"}, HTTPStatus.NOT_FOUND
        
        response = {
            "total_Urls": Url.total_urls(authenticated_user.email),
            "total_Clicks": Url.total_clicks(authenticated_user.email), 
        }

        return response, HTTPStatus.OK  
   

# @url_namespace.route('/date') 
# class GetLatestURLSApiView(Resource):
   
#    @url_namespace.doc(description = "Get more information about urls") 
#    @url_namespace.marshal_list_with(url_marshall_serializer)       
#    @jwt_required()
     
#    def get(self):
#       authenticated_user_email = get_jwt_identity() 
#       authenticated_user = User.query.filter_by(email=authenticated_user_email).first()
         
#       if not authenticated_user:
#          return {"message": "User not found"}, HTTPStatus.NOT_FOUND

#       urls = Url.query.filter_by(creator = authenticated_user.email).order_by(Url.created.desc()).limit(5).all()  
#       return urls, HTTPStatus.OK   


@url_namespace.route('/<url_uuid>/qrcode')
class GenerateURLQrCodeApiView(Resource):
   
    @url_namespace.doc(description = "Get Analytics") 
    @jwt_required()
       
    def get(self, url_uuid ):
        authenticated_user_email = get_jwt_identity() 
      
        authenticated_user = User.query.filter_by(email = authenticated_user_email).first()
           
        if not authenticated_user:
            return {"message": "User not found"}, HTTPStatus.NOT_FOUND

        url = Url.query.filter_by(creator = authenticated_user.email).all()
        img = qrcode.make(url_uuid)
        img_io = io.BytesIO()
        img.save(img_io, 'PNG')
        img_io.seek(0)
      
        return send_file(img_io, mimetype='image/png', as_attachment = True, attachment_filename='qrcode.png')


