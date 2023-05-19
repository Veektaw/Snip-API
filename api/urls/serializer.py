from flask_restx import Namespace, fields


url_namespace = Namespace('url', description='Namespace for urls')

url_expect_serializer = url_namespace.model ( 
    'Url', {
      'user_long_url' : fields.String(required=True , description="User's provided long url"),
    }
)


url_marshall_serializer = url_namespace.model (
    'Short_Url',{
      'user_long_url' : fields.String(required=True , description="User's long url"),
      'short_url' : fields.String(required=True , description='Short url provided'),
      'url_title' : fields.String(required=True , description="User's long url title"),
      'creator' : fields.String(required=True , description="User's long url title"),
      'visited' : fields.Integer(required=True , description='Number of clicks'),
      'created' : fields.DateTime()
   }
)