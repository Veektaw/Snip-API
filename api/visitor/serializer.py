from flask_restx import Namespace, fields

visitor_namespace = Namespace('visitor', description='Namespace for visitors')


url_expect_serializer = visitor_namespace.model ( 
    'Url', {
      'user_long_url' : fields.String(required=True , description="User's provided long url"),
    }
)


url_marshall_serializer = visitor_namespace.model (
    'Short_Url',{
      'user_long_url' : fields.String(required=True , description="User's long url"),
      'short_url' : fields.String(required=True , description='Short url provided'),
      'url_title' : fields.String(required=True , description="User's long url title"),
      'creator' : fields.String(required=True , description="User's long url title"),
      'visited' : fields.Integer(required=True , description='Number of clicks'),
      'created' : fields.DateTime()
   }
)