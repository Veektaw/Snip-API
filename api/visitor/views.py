from .serializer import visitor_namespace, url_expect_serializer
import logging
from http import HTTPStatus
from flask_restx import Resource
from flask import request
from api.helpers.url_validator import URLCreator
from ..utility import limiter




@visitor_namespace.route('/create')
class VisitorCreateURL(Resource):

    @visitor_namespace.expect(url_expect_serializer)
    @visitor_namespace.doc(description="Make a url short",
                           params={"user_long_url": "Long url by the user"})
    @limiter.limit("10/minute")
     
    def post(self):
       
        """
        Create a short URL. User provides long url, and it is shortened.
        """
        
        logger = logging.getLogger(__name__)
        logger.info("VisitorCreateURL is called")
       
        data = request.get_json()
        user_long_url = data.get('user_long_url')
      
        if URLCreator.is_valid_url(user_long_url):
            url_title = URLCreator.extract_url_data(user_long_url)
            short_url = URLCreator.short_url(user_long_url)
         
            short_url_data = {
                "user_long_url": user_long_url,
                "short_url": short_url,
                "url_title": url_title
            }
         
            logger.debug(f"Visitor short url: {short_url_data} is created")
            return short_url_data, HTTPStatus.CREATED  
    
        logger.warning("This is not a valid URL")
        response = {"message": "This is not a valid URL"}
        
        return response, HTTPStatus.BAD_REQUEST
