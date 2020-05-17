from flask_restful import fields
from sqlalchemy.sql import func
from sqlalchemy.sql.expression import text
from datetime import datetime

from sqlalchemy import Table, Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import backref
from blueprints import db


class Users(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)

    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    avatar = db.Column(db.String(255))
    address = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(13), nullable=False, unique=True)

    status = db.Column(db.String(20), nullable=False, default="buyer")
    salt = db.Column(db.String(255))
    created_at = db.Column(db.DateTime(timezone=True),
                           server_default=func.now())
    updated_at = db.Column(db.DateTime(timezone=True), onupdate=func.now())

    cart = db.relationship(
        'Carts', backref='buyers', lazy=True, uselist=False, cascade="all, delete-orphan")

    response_fields = {
        'id': fields.Integer,
        'username': fields.String,
        'password': fields.String,
        'name': fields.String,
        'email': fields.String,
        'avatar': fields.String,
        'address': fields.String,
        'phone': fields.String,
        'status': fields.String
    }

    jwt_user_fields = {
        'id': fields.Integer,
        'username': fields.String,
        'status': fields.String
    }

    def __init__(self, username, password, name, email,
     avatar, 
     address, phone, status, salt):
        self.username = username
        self.password = password
        self.name = name
        self.email = email
        self.avatar = avatar
        self.address = address
        self.phone = phone
        self.status = status
        self.salt = salt

    def __repr__(self):
        return '<User %r>' % self.id
