from blueprints import db
from flask_restful import fields
from sqlalchemy.sql import func
from sqlalchemy.sql.expression import text
from datetime import datetime

from sqlalchemy import Table, Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import backref


class Games(db.Model):
    __tablename__ = "games"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    tile = db.Column(db.String(255), default='')
    banner = db.Column(db.String(255), default='')
    publisher = db.Column(db.String(20), nullable=False)
    description = db.Column(db.Text , nullable=False)
    category = db.Column(db.String(100), nullable=False)
    gplay = db.Column(db.String(255),nullable=True)
    appstore = db.Column(db.String(255),nullable=True)
    website = db.Column(db.String(255), nullable=True)
    community = db.Column(db.String(255) ,nullable=True)
    promo = db.Column(db.Boolean, default=False, server_default="false")
    discount = db.Column(db.Integer, default=0)
    sold = db.Column(db.Integer, default=0)
    # seller_id = db.Column(db.Integer, db.ForeignKey('sellers.id'))

    voucher = db.relationship(
        'GameVouchers', backref='games', lazy=True, uselist=False, cascade="all, delete-orphan")
    cart = db.relationship(
        'Carts', backref='games', lazy=True, uselist=False, cascade="all, delete-orphan")

    created_at = db.Column(db.DateTime(timezone=True),
                           server_default=func.now())
    updated_at = db.Column(db.DateTime(timezone=True), onupdate=func.now())

    response_fields = {
        'id': fields.Integer,
        'name': fields.String,
        'tile': fields.String,
        'banner': fields.String,
        'publisher': fields.String,
        'description': fields.String,
        'category': fields.String,
        'gplay': fields.String,
        'appstore': fields.String,
        'website': fields.String,
        'community': fields.String,
        'promo': fields.Boolean,
        'discount': fields.Integer,
        'sold': fields.Integer
    }

    def __init__(self, name, tile, banner, publisher, description,
                 category, gplay, appstore, website, community,
                 promo, discount
                 #  ,sold
                 ):
        self.name = name
        self.tile = tile
        self.banner = banner
        self.publisher = publisher
        self.description = description
        self.category = category
        self.gplay = gplay
        self.appstore = appstore
        self.website = website
        self.community = community
        self.promo = promo
        self.discount = discount
        # self.sold = sold

    def __repr__(self):
        return '<Games %r>' % self.id


class GameVouchers(db.Model):
    __tablename__ = "game_vouchers"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    game_id = db.Column(db.Integer, db.ForeignKey('games.id'))
    voucher = db.Column(db.String(255), nullable=False)
    price = db.Column(db.String(255), default='')

    transaction_details = db.relationship(
        'TransactionDetails', backref='game_vouchers', lazy=True, uselist=False, cascade="all, delete-orphan")

    created_at = db.Column(db.DateTime(timezone=True),
                           server_default=func.now())
    updated_at = db.Column(db.DateTime(timezone=True), onupdate=func.now())

    response_fields = {
        'id': fields.Integer,
        'game_id': fields.Integer,
        'voucher': fields.String,
        'price': fields.Integer
    }

    def __init__(self, game_id, voucher, price):
        self.game_id = game_id
        self.voucher = voucher
        self.price = price

    def __repr__(self):
        return '<GameVouchers %r>' % self.id
