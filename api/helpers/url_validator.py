import random
import string
from api.models.url import Url
from flask import request 
from urllib.error import URLError, HTTPError
import re

def check_valid_url(url):
    
    regex = re.compile(
        r'^(?:http|ftp)s?://'  # scheme
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or IP
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    
    return bool(regex.match(url))


class URLCreator:

    @classmethod
    def short_url(cls):
        characters_combinantion = string.ascii_letters + string.digits
        random_string_combination = ''.join(random.choices(characters_combinantion, k=5))
        new_url = f"https://{request.host}/{random_string_combination}"
        does_url_exist = Url.check_url(new_url)
        
        if does_url_exist: 
            URLCreator.short_url()
            return new_url
    

    @classmethod
    def is_valid_url(cls, url): 
        """"Check if a url is valid or not"""
        regex = re.compile(
            r'^(?:http|ftp)s?://'  # scheme
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
            r'localhost|'  # localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or IP
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        return bool(regex.match(url)) 

    @classmethod
    def extract_url_data(cls, url): 
        from bs4 import BeautifulSoup
        import requests
        # Make a GET request to the URL
        response = requests.get(url)

        # Parse the HTML content of the page using BeautifulSoup
        soup = BeautifulSoup(response.content, 'html.parser')

        # Extract the title of the page
        try:
            title = soup.title.string
        except:
            title = ''

        # Extract the description of the page
        return title

