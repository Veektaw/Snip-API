from flask_restx import Namespace, fields

manage_namespace = Namespace('manage', 'User account managementnamespace' ,path='/manage') 


password_reset_mail = manage_namespace.model(
   'User', {
      'email' : fields.String(required=True , description='An email address'),
   }
)

password_reset_confirm = manage_namespace.model(
   'User', {
      'password1' : fields.String(required=True , description='New Password'),
      'password2' : fields.String(required=True , description='Confirm password'),
   }
)

password_change = manage_namespace.model(
   'User', {
      'old_password' : fields.String(required=True , description='Current Password'),
      'new_password' : fields.String(required=True , description='New Password'),
      'confirm_password' : fields.String(required=True , description='Confirm password'),
   }
)

user_serializer = manage_namespace.model(
    'User', {
      'id': fields.String(), 
      'first_name' : fields.String(required=True , description='First Name'),
      'last_name' : fields.String(required=True , description='Last Name'),
      'email' : fields.String(required=True , description='An email address'), 
      'created' : fields.DateTime()
   }
)