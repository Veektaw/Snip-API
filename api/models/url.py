from ..utility import db
import random
import string
from datetime import datetime
from uuid import uuid4


class Url(db.Model):
    __tablename__  = 'urls'

    id = db.Column(db.Integer(), primary_key=True)
    uuid = db.Column(db.String(length=60), nullable=False,  unique=True)
    user_long_url = db.Column(db.String(300), nullable=False)
    qr_code_url = db.Column(db.String(300), nullable=True, unique=True)
    custom_url = db.Column(db.String(300), nullable=True, unique=True)
    short_url = db.Column(db.String(300), nullable=True, unique=True)
    created = db.Column(db.DateTime() , nullable=False , default=datetime.utcnow)
    url_title = db.Column(db.String(300), nullable=True)
    visited = db.Column(db.Integer(), default=0)
    creator = db.Column(db.Integer(), db.ForeignKey('users.id') , nullable=False)

    def __repr__(self):
        return f"<url {self.id}>"
    
    def save(self):
        self.uuid = uuid4().hex
        db.session.add(self)
        db.session.commit()

    @classmethod
    def get_by_id(cls, uuid):
        return cls.query.get_or_404(uuid)
    
    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    @classmethod
    def total_clicks(cls, id):
        urls = Url.query.filter_by(creator = id).all()
        total_url_clicks = sum([url.visited for url in urls])
        return total_url_clicks 
    
    @classmethod
    def total_urls(cls, id):
        return Url.query.filter_by(creator = id).count() 

    @classmethod
    def check_url(cls , url):
        url_exists = cls.query.filter_by(short_url = url).first()
        return True if url_exists else False