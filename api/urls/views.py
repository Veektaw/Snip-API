import qrcode
import base64
import io
import logging
from http import HTTPStatus
from flask_restx import Resource 
from flask import request, Response, send_file, redirect, make_response, current_app, session
from flask_jwt_extended import jwt_required , get_jwt_identity
from .serializer import (url_expect_serializer, url_marshall_serializer,
                         url_custom_expect_serializer,
                         url_custom_marshall_serializer,
                         url_namespace)
from ..utility import db, cache, limiter
from api.helpers.url_validator import URLCreator
from api.models.user import User
from api.models.url import Url
from api.auth.views import DateTimeEncoder
 

@url_namespace.route('/create')
class CreateURL(Resource):
   
    @url_namespace.expect(url_expect_serializer)     
    @url_namespace.marshal_with(url_marshall_serializer)
    @url_namespace.doc(description = "Make a url short",
                      params={"user_long_url":"Long url by the user"})   
    @jwt_required()
    @cache.cached(timeout=50)
    @limiter.limit("10/minute")
     
    def post(self):
       
        """
    
            Create a short URL. User provides long url, and it is shortened.
    
        """
        
        
        logger = logging.getLogger(__name__)
        logger.info("CreateURL is called")
       
        current_user = get_jwt_identity() 
        authenticated_user = User.query.filter_by(email=current_user).first()  
       
        if not authenticated_user:
            logger.error("User not found")
            return {"message": "User not found"}, HTTPStatus.NOT_FOUND     
       
        data = request.get_json()
        user_long_url = data.get('user_long_url')
      
        if URLCreator.is_valid_url(user_long_url):
            url_title = URLCreator.extract_url_data(user_long_url)
            short_url = URLCreator.short_url(user_long_url)
         
            url = Url (
                user_long_url = user_long_url,
                short_url = short_url,
                url_title = url_title,
                creator = authenticated_user.email)
         
            try:
                url.save()
                logger.info(f"Custom URL by {authenticated_user} is saved to the database")
            
            except:
                logger.exception("Error loading")
                db.session.rollback()
                
                response = {"message": "Error loading"}
                logger.error("Error loading information")
                 
                return response , HTTPStatus.INTERNAL_SERVER_ERROR 
        
            logger.debug(f"Created a short url: {url}")
            
            return url, HTTPStatus.OK  
        
        response = {"message": "This is not a valid URL"}
        logger.warning("User provides invalid URL")
        
        return response, HTTPStatus.BAD_REQUEST
   


@url_namespace.route('/custom')
class CreateCustomURL(Resource):
   

    @url_namespace.expect(url_custom_expect_serializer)     
    @url_namespace.marshal_with(url_custom_marshall_serializer)
    @url_namespace.doc(description = "Make a custom url",
                      params={"user_long_url":"Long url by the user",
                              "custom_url": "User provides a custom url"})  
    @jwt_required()
    @cache.cached(timeout=50)
    @limiter.limit("10/minute")
     
    def post(self):
       
        """
    
            Create a custom URL. User provides long url, and it is shortened.
    
        """
        logger = logging.getLogger(__name__)
        logger.info("CreateCustomURL is called")
       
        current_user = get_jwt_identity() 
        authenticated_user = User.query.filter_by(email=current_user).first()  
       
        if not authenticated_user:
            logger.error("User not found")
            return {"message": "User not found"}, HTTPStatus.NOT_FOUND     
       
        data = request.get_json()
        user_long_url = data.get('user_long_url')
        custom_url = data.get('custom_url')
      
        if URLCreator.is_valid_url(user_long_url):
            url_title = URLCreator.extract_url_data(user_long_url)
            custom_url = URLCreator.custom_url(user_long_url, custom_url)
         
            url = Url (
                user_long_url = user_long_url,
                custom_url = custom_url,
                url_title = url_title,
                creator = authenticated_user.email
            )
         
            try:
                url.save()
                logger.info(f"Custom URL by {authenticated_user} is saved to the database")
            
            except:
                logger.exception("Error loading")
                db.session.rollback()
                response = {"message": "Error loading"} 
                return response , HTTPStatus.INTERNAL_SERVER_ERROR
             
            logger.debug(f"Created custom url: {url}")
            return url, HTTPStatus.OK  
    
        logger.warning("This is not a valid URL")
        response = {"message": "This is not a valid URL"}
        return response, HTTPStatus.BAD_REQUEST




@url_namespace.route('/urls') 
class GetURLS(Resource):
   
    
    @url_namespace.doc(description = "Get all URLS",
                       params = {"get method":"Get all URLs"})
    @url_namespace.marshal_with(url_marshall_serializer)  
    @jwt_required()
    @cache.cached(timeout=50)
    @limiter.limit("5 per minute")

    def get(self):

        """
    
        Get all URLS, with a simple get method.
    
        """
        
        logger = logging.getLogger(__name__)
        logger.info("GetURLS endpoint called")

        authenticated_user_email = get_jwt_identity() 

        authenticated_user = User.query.filter_by(email = authenticated_user_email).first()
          
        if not authenticated_user:
            logger.warning("User not found")
            return {"message": "User not found"}, HTTPStatus.NOT_FOUND
            
        
        url = Url.query.filter_by(creator=authenticated_user.email).all()
        logger.debug(f"{authenticated_user} Retrieved {len(url)} URLs")

        return url, HTTPStatus.OK
    
    
@url_namespace.route('/<id>')
class ViewDeleteURLbyID(Resource):
    
    @url_namespace.doc(description = "Get a URL by id",
                       params = {"id":"UUID of the URL"})
    @url_namespace.marshal_with(url_marshall_serializer)  
    @jwt_required()
    @cache.cached(timeout=50)
    @limiter.limit('3 per minute', key_func = lambda : session.get("id"))
       
    def get(self, id):
        
        """
        
            This enables the user view a particular URL
        
        """
        
        logger = logging.getLogger(__name__)
        logger.info("ViewDeleteURLbyID a URL by UUID called")
        
        authenticated_user_email = get_jwt_identity() 
      
        authenticated_user = User.query.filter_by(email = authenticated_user_email).first()
           
        if not authenticated_user:
            logger.warning("URL not found")
            return {"message": "URL not found"}, HTTPStatus.NOT_FOUND
        
        url = Url.get_by_id(id)
        logger.debug(f"Retrieved {url} URL by UUID")
        
        return url, HTTPStatus.OK
    
    
    @url_namespace.doc(description = "Get a URl by UUID",
                       params = {"id":"UUID of the URL"})
    @jwt_required()
    @cache.cached(timeout=50)
    @limiter.limit("10/minute")
    
    def delete(self, id):
        
        """
        
            This deletes a URL of a particular user.
        
        """
        
        logger = logging.getLogger(__name__)
        logger.info("Delete a URL by UUID called")
        
        authenticated_user_email = get_jwt_identity() 
      
        authenticated_user = User.query.filter_by(email = authenticated_user_email).first()
           
        if not authenticated_user:
            logger.warning("URL not found")
            return {"message": "URL not found"}, HTTPStatus.NOT_FOUND
        
        url = Url.get_by_id(id)
        
        url.delete()
        logger.debug(f"Deleted {url} URL")
        
        return url, HTTPStatus.OK


@url_namespace.route('/<short_url>/visited')
class ShortUrlRedirect(Resource):
    
    @url_namespace.doc(description = "Add clicks to a created short URL",
                       params = {"short_url":"Clicks"})
    @jwt_required()
    @cache.cached(timeout=50)
    @limiter.limit("10/minute")
    
    def get(self, short_url):
        url = Url.query.filter_by(short_url=short_url).first()
        
        logger = logging.getLogger(__name__)
        logger.info("ShortURLRedirect is called")

        if url is None:
            logger.error("Invalid short URL")
            return {"message": "Invalid short URL"}, HTTPStatus.BAD_REQUEST

        url.visited += 1
        db.session.commit()

        return redirect(url.user_long_url)


@url_namespace.route('/info') 
class GetURLSInfo(Resource):
   
    @url_namespace.doc(description= "Get infomation about urls",
                       params = {"id":"This provides more information about the URLS"})    
    @jwt_required()
    @cache.cached(timeout=50)
    @limiter.limit("10/minute")
    
    def get(self):
        
        logger = logging.getLogger(__name__)
        logger.info("GetURLSInfo is called")
        
        authenticated_user_email = get_jwt_identity() 
        authenticated_user = User.query.filter_by(email = authenticated_user_email).first()
           
        if not authenticated_user:
            logger.warning("User not found")
            return {"message": "User does not exist"}, HTTPStatus.NOT_FOUND
        
        response = {
            "total_Urls": Url.total_urls(authenticated_user.email),
            "total_Clicks": Url.total_clicks(authenticated_user.email), 
        }
        logger.debug(f"Info {response} of URL")
        
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


@url_namespace.route('/<id>/qrcode')
class GenerateURLQRCode(Resource):
   
    @url_namespace.doc(description = "Get QR code of a short URL",
                       params={"id": "UUID of the short URL created earlier"}) 
    @jwt_required()
    @cache.cached(timeout=50)
    @limiter.limit("10/minute")
       
    def get(self, id):
        
        logger = logging.getLogger(__name__)
        logger.info("GenerateURLQRCode is called")
        
        authenticated_user_email = get_jwt_identity() 
      
        authenticated_user = User.query.filter_by(email = authenticated_user_email).first()
           
        if not authenticated_user:
            return {"message": "User not found"}, HTTPStatus.NOT_FOUND

        url = Url.query.filter_by(id=id, creator=authenticated_user.email).first()
        img = qrcode.make(id)
        img_io = io.BytesIO()
        img.save(img_io, 'PNG')
        img_io.seek(0)
        
        image_data = base64.b64encode(img_io.getvalue()).decode('utf-8')
        url.qr_code_url = image_data
        url.save()
      
        response = make_response(send_file(img_io, mimetype='image/png'))
        response.headers['Content-Disposition'] = f'attachment; filename=qrcode_{url.id}.png'
        
        logger.debug(f"QR code {response} created")
        
        return response, HTTPStatus.CREATED


