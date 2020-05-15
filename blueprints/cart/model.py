from blueprints import db
from flask_restful import fields
from sqlalchemy.sql import func
from sqlalchemy.sql.expression import text
from datetime import datetime

from sqlalchemy import Table, Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import backref


class Carts(db.Model):
    __tablename__ = "carts"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    game_id = db.Column(db.Integer, db.ForeignKey("games.id"))
    item_price = db.Column(db.Integer, default=0)
    payment_id = db.Column(db.Integer, db.ForeignKey("payments.id"))
    # payment_id = db.Column(db.Integer)
    payment_status = db.Column(db.Boolean, default=False)
    total_price = db.Column(db.Integer, default=0)
    status = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.now())
    updated_at = db.Column(db.DateTime, default=datetime.now())
    transaction_details = db.relationship(
        'TransactionDetails', backref='carts', lazy=True, uselist=False, cascade="all, delete-orphan")

    response_fields = {
        "id": fields.Integer,
        "user_id": fields.Integer,
        "game_id": fields.Integer,
        "item_price": fields.Integer,
        "payment_id": fields.Integer,
        "payment_status": fields.Boolean,
        "status": fields.Boolean
    }

    def __init__(self, user_id, game_id):
        self.user_id = user_id
        self.game_id = game_id

    def __repr__(self):
        return "<Carts %r>" % self.id


class Payments(db.Model):
    __tablename__ = "payments"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    payment_method = db.Column(db.String(255), default='')
    account_name = db.Column(db.String(255), default='')
    account_number = db.Column(db.String(255), default='')
    status = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.now())
    updated_at = db.Column(db.DateTime, default=datetime.now())
    cart = db.relationship(
        'Carts', backref='payments', lazy=True, uselist=False, cascade="all, delete-orphan")

    response_fields = {
        "created_at": fields.DateTime,
        "updated_at": fields.DateTime,
        "id": fields.Integer,
        "payment_method": fields.String,
        "account_name": fields.String,
        "account_number": fields.String,
        "status": fields.Boolean
    }

    def __init__(self, payment_method, account_name, account_number):
        self.payment_method = payment_method
        self.account_number = account_number
        self.account_name = account_name

    def __repr__(self):
        return "<Payments %r>" % self.id


class TransactionDetails(db.Model):
    __tablename__ = "transactiondetails"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    cart_id = db.Column(db.Integer, db.ForeignKey("carts.id"))
    voucher_id = db.Column(db.Integer, db.ForeignKey("game_vouchers.id"))
    price = db.Column(db.Integer, default=0)
    quantity = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.now())
    updated_at = db.Column(db.DateTime, default=datetime.now())

    response_fields = {
        "id": fields.Integer,
        "cart_id": fields.Integer,
        "voucher_id": fields.Integer,
        "price": fields.Integer,
        "quantity": fields.Integer,
        "created_at": fields.DateTime,
        "updated_at": fields.DateTime,
    }

    def __init__(self, cart_id, voucher_id, price, quantity):
        self.cart_id = cart_id
        self.voucher_id = voucher_id
        self.price = price
        self.quantity = quantity

    def __repr__(self):
        return "<TransactionDetails %r>" % self.id
