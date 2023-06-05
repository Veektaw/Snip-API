from api.models.user import User
from api.utility import db, admin
from flask_admin.contrib.sqla import ModelView


class UserView(ModelView):
    pass