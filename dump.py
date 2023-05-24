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
    
    
    
    
# SCOPES = [
#         "https://www.googleapis.com/auth/gmail.send"
#     ]


# flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
# creds = flow.run_local_server(port=0)

# service = build('gmail', 'v1', credentials=creds)
# message = MIMEText('This is the body of the email')
# message['to'] = 'recipient@gmail.com'
# message['subject'] = 'Email Subject'
# create_message = {'raw': base64.urlsafe_b64encode(message.as_bytes()).decode()}

# try:
#     message = (service.users().messages().send(userId="me", body=create_message).execute())
#     print(F'sent message to {message} Message Id: {message["id"]}')
# except HTTPError as error:
#     print(F'An error occurred: {error}')
#     message = None




# def send_sign_two_factor_authentication_mail(*args , **kwargs):
        
#         receiver = kwargs['email']
#         code = kwargs['code']
#         subject = "Login attempt"
#         body = f"""
#                 We received a login request on ypur account\n
#                 \n
#                 You can ignore if you did not make this request.\n
#                 CODE : {code}
#             """

#         em = EmailMessage()
#         em["From"] = sender
#         em["To"] = receiver
#         em["subject"] = subject
#         em.set_content(body)
#         context = ssl.create_default_context()

#         try:
#             with smtplib.SMTP_SSL("smtp.gmail.com", port=465, context=context) as connection:
#                 connection.login(sender, password)
#                 connection.sendmail(sender, receiver, em.as_string())
#         except:
#             pass
#         return True