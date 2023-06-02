from ..utility import db
from sqlalchemy import text
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
from uuid import uuid4
from flask_uuid import uuid



class User(db.Model):
    __tablename__  = 'users'

    id = db.Column('id', db.Text(length=36), default=lambda: str(uuid.uuid4()), primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True)
    password = db.Column(db.Text(), nullable=False)
    url_created = db.relationship('Url' , backref='url_creator' )
    token = db.relationship('Token' , backref='user_token' , lazy=True)

    def __repr__(self):
        return f"<user {self.email}>"
    
    def save(self):
        db.session.add(self)
        db.session.commit()

    @classmethod
    def get_by_id(cls, id):
        return cls.query.get_or_404(id)
    
    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def update(self):
        db.session.commit()
        
        
        
class Token(db.Model):
    __tablename__  = 'tokens'
    
    id = db.Column('id', db.Text(length=36), default=lambda: str(uuid.uuid4()), primary_key=True)
    token = db.Column(db.Text(), nullable=False)
    token_type = db.Column(db.String(length=20), nullable=False)
    created = db.Column(db.DateTime() , nullable=False , default=datetime.utcnow)
    user_id =  db.Column(db.Integer(), db.ForeignKey('users.id'))
    
    
    def __repr__(self):
        return f"<user {self.token}>"


    def save(self):
        db.session.add(self)
        db.session.commit()


    def delete(self):
        db.session.delete(self)
        db.session.commit()

