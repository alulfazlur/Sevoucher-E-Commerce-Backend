import json
import hashlib
import uuid
from datetime import datetime
from blueprints import db, app, buyer_required, seller_required

from flask import Blueprint
from flask_restful import Resource, Api, reqparse, marshal, inputs
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required, get_jwt_claims
from sqlalchemy import desc

from .model import Carts, TransactionDetails
from blueprints.game.model import GameVouchers, Games

bp_cart = Blueprint('cart', __name__)
api = Api(bp_cart)


class CartResource(Resource):

    @buyer_required
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument("voucher_id", location="json")
        parser.add_argument("payment_id", location="json",
                            choices=('pulsa', 'transfer'))

        args = parser.parse_args()
        voucher = GameVouchers.query.get(args["voucher_id"])

        if voucher is None:
            return {'message': 'Voucher Game tidak ada'}, 404

        claims = get_jwt_claims()
        user_id = claims['id']

        cart = Carts.query.filter_by(user_id=user_id)
        game_id = voucher.game_id
        cart = cart.filter_by(game_id=game_id)

        if cart is None:
            cart = Carts(user_id, game_id, args["payment_id"])
            db.session.add(cart)
            db.session.commit()

        td = TransactionDetails(
            cart.id, args["voucher_id"], voucher.price)
        db.session.add(td)
        db.session.commit()

        game = Games.query.get(game_id)
        if game.promo:
            cart.item_price += ((int(voucher.price) -
                                 (int(game.discount)*int(voucher.price))))
        else:
            cart.item_price += (int(voucher.price))

        cart.updated_at = datetime.now()
        db.session.commit()

        return {'status': 'Success'}, 200

    @buyer_required
    def get(self, id):
        claims = get_jwt_claims()
        user_id = claims['id']
        qry = Carts.query.get(user_id)
        if qry is not None:
            return marshal(qry, Carts.response_fields), 200
        return {'status': 'NOT_FOUND'}, 404


api.add_resource(CartResource, '')
