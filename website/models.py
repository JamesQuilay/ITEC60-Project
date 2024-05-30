from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func
from sqlalchemy import Table, Column, Integer, ForeignKey
from werkzeug.security import check_password_hash
from datetime import datetime


# Association Table for many-to-many relationship between Note and Tag
note_tags_association = Table('note_tags_association', db.Model.metadata,
    Column('note_id', Integer, ForeignKey('note.id')),
    Column('tag_id', Integer, ForeignKey('tag.id'))
)


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    first_name = db.Column(db.String(150))
    is_admin = db.Column(db.Boolean, default=False)
    notes = db.relationship('Note', backref='user', lazy=True, cascade='all, delete-orphan')
    categories = db.relationship('Category', backref='user', lazy=True, cascade='all, delete-orphan')

    def check_password(self, password):
        return check_password_hash(self.password, password)


class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    content = db.Column(db.String(10000))
    timestamp = db.Column(db.DateTime, default=func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'))
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    tag_id = db.Column(db.Integer, db.ForeignKey('tag.id'))
    is_pinned = db.Column(db.Boolean, default=False)
    tags = db.relationship('Tag', secondary=note_tags_association, backref='notes', lazy='dynamic')

    def update_timestamp(self):
        self.updated_timestamp = datetime.utcnow()
    

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=True, unique=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'))
    notes = db.relationship('Note', backref='category', lazy=True)


class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), unique=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'))