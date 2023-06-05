from ..utility import db
from datetime import datetime
from flask_uuid import uuid


class TokenBlocklist(db.Model):
    
    __tablename__  = 'token_blocklists'
    
    id = db.Column(db.Integer, primary_key=True)
    jti = db.Column(db.String(36), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)
