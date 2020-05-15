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
    def options(self, id=None):
        return {'status': 'ok'}, 200

    @buyer_required
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument("voucher_id", location="json")
        parser.add_argument("quantity", location="json")
        args = parser.parse_args()

        voucher = GameVouchers.query.get(args["voucher_id"])
        if voucher is None:
            return {'message': 'Voucher Game tidak ada'}, 404

        claims = get_jwt_claims()
        user_id = claims['id']

        cart = Carts.query.filter_by(user_id=user_id).first()
        game_id = voucher.game_id
        cart = cart.filter_by(game_id=game_id).first()

        if cart is None:
            cart = Carts(user_id, game_id)
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
    def get(self):
        claims = get_jwt_claims()
        cart = Carts.query.filter_by(user_id=claims["id"])
        cart = cart.filter_by(status=True)
        cart = cart.order_by(desc(Carts.updated_at))
        cart = cart.all()
        result = []
        for qry in cart:
            game = Games.query.filter_by(id=qry.game_id).first()
            marshalGame = marshal(game, Games.response_fields)
            marshalqry = marshal(qry, Carts.response_fields)
            marshalqry["gane_id"] = marshalGame
            transactiondetail = TransactionDetails.query.filter_by(
                cart_id=qry.id)
            transactiondetail = transactiondetail.all()
            list_td = []
            for td in transactiondetail:
                voucher = GameVouchers.query.filter_by(
                    id=td.voucher_id).first()
                marshalVoucher = marshal(voucher, GameVouchers.response_fields)
                marshaltd = marshal(td, TransactionDetails.response_fields)
                marshaltd["voucher_id"] = marshalVoucher
                list_td.append(marshaltd)
            result.append({"cart": marshalqry, "transaction_detail": list_td})
        return result, 200

    @buyer_required
    def delete(self, id=None):
        claims = get_jwt_claims()
        cart = Carts.query.filter_by(user_id=claims["id"])
        cart = cart.filter_by(status=True)
        qry = TransactionDetails.query.get(id)
        if qry is None:
            return {'status': 'NOT_FOUND'}, 404

        cart = cart.filter_by(id=qry.cart_id).first()
        if cart is None:
            return {'status': 'Access denied'}, 400

        # hard delete
        db.session.delete(qry)
        db.session.commit()
        return {"message": 'Deleted'}, 200


api.add_resource(CartResource, "", "/<int:id>")
