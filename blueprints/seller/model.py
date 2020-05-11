from blueprints import db
from flask_restful import fields
from sqlalchemy.sql import func
from sqlalchemy.sql.expression import text
from datetime import datetime

from sqlalchemy import Table, Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import backref


class Sellers(db.Model):
    __tablename__ = "sellers"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    bank_account = db.Column(db.Integer, nullable=False)
    email = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.Integer, nullable=False)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    game = db.relationship(
        'Games', backref='sellers', lazy=True, uselist=False, cascade="all, delete-orphan")

    created_at = db.Column(db.DateTime(timezone=True),
                           server_default=func.now())
    updated_at = db.Column(db.DateTime(timezone=True), onupdate=func.now())

    response_fields = {
        'id': fields.Integer,
        'name': fields.String,
        'email': fields.Integer,
        'address': fields.String,
        'phone': fields.Integer,
        'user_id': fields.Integer
    }

    def __init__(self, name, email, address, phone, user_id):
        self.name = name
        self.email = email
        self.address = address
        self.phone = phone
        self.user_id = user_id

    def __repr__(self):
        return '<Sellers %r>' % self.id
