from flask_restx import Namespace, fields

auth_namespace = Namespace('auth', description='Namespace for authentication')


signup_expect_model = auth_namespace.model(
    'User',{
        'first_name': fields.String(description='First name of the student', required=True,),
        'last_name': fields.String(description='Last name of the student', required=True),
        'email': fields.String(description="Email of student", required=True),
        'password': fields.String(description='Password of student', required=True)                          
    }
)


signup_model = auth_namespace.model(
    'UserSignup',{
        'id': fields.Integer(description='An order ID'),
        'first_name': fields.String(description='First name of the student', required=True,),
        'last_name': fields.String(description='Last name of the student', required=True),
        'email': fields.String(description="Email of student", required=True),
        'password': fields.String(description='Password of student', required=True)                          
    }
)


login_expect_model = auth_namespace.model(
    'UserLogin',{
        'email': fields.String(description="Email of student", required=True),
        'password': fields.String(description='Password of student', required=True)                          
    }
)