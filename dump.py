from flask import Flask, request
from flask_restx import Resource, Api, fields
import random
import string

app = Flask(__name__)
api = Api(app)

url_model = api.model('Url', {
    'long_url': fields.String(description='Original URL', required=True)
})

def generate_short_code(length):
    """Generate a random short code with given length"""
    letters = string.ascii_lowercase + string.digits
    return ''.join(random.choice(letters) for i in range(length))

def shorten_url(long_url):
    """Generate a shortened URL with random code"""
    short_code = generate_short_code(6) # generate a 6-character code
    short_url = request.host_url + short_code
    # store the mapping from short code to long URL in a database
    # for simplicity, we'll just print it out here
    print(f'Mapping {short_code} to {long_url}')
    return short_url

@api.route('/shorten_url')
class UrlShortener(Resource):
    @api.expect(url_model)
    def post(self):
        """Shorten a given URL"""
        long_url = request.json.get('long_url')
        if not long_url:
            return {'message': 'Missing URL parameter'}, 400
        short_url = shorten_url(long_url)
        return {'short_url': short_url}, 200

if __name__ == '__main__':
    app.run(debug=True)
    
    
    #'id', db.Text(length=36), default=lambda: str(uuid.uuid4()), primary_key=True