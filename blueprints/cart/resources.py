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
        parser.add_argument("ign", location="json", required=True)
        parser.add_argument("game_name", location="json")
        parser.add_argument("voucher_name", location="json", required=True)
        args = parser.parse_args()

        game = Games.query.filter_by(name=args["game_name"]).first()
        gameId = game.id
        voucher = GameVouchers.query.filter_by(game_id=gameId, voucher=args["voucher_name"]).first()
        #  cek apakah game mempunyai voucher tersebut
        if voucher is None:
            return {'message': 'Voucher Game tidak ada'}, 404

        claims = get_jwt_claims()
        user_id = claims['id']

        game_id = voucher.game_id
        cart = Carts.query.filter_by(user_id=user_id, game_id=game_id, status=True).first()

        if cart is None:
            cart = Carts(user_id, gameId)
            db.session.add(cart)
            db.session.commit()


        tdetails = TransactionDetails.query.filter_by(cart_id = cart.id, game_id=gameId, ign=args["ign"], voucher_id = voucher.id).first()
        if tdetails is None:
            # jika voucher tidak ada di transdet
            td = TransactionDetails(cart.id, gameId, args["ign"], voucher.id, 1, 0)
            db.session.add(td)
            db.session.commit()

        else :
            # jika voucher ada di transdet
            tdetails.quantity += 1
            db.session.commit()

        tdetails = TransactionDetails.query.filter_by(cart_id = cart.id, game_id=gameId, ign=args["ign"], voucher_id = voucher.id).first()
        if game.promo:
            price = ((int(voucher.price) - (int(game.discount)/100*int(voucher.price))))
            tdetails.price += price
            db.session.commit()

        else:
            price = (int(voucher.price))
            tdetails.price += price
            db.session.commit()

        cart_item = Carts.query.filter_by(user_id=user_id, game_id=game_id, status=True).first()

        cart_item.total_price_item += price
        cart_item.updated_at = datetime.now()
        db.session.commit()

        carts = Carts.query.filter_by(user_id=user_id, status=True).all()
        total = 0
        for cart in carts:
            total += cart.total_price_item
        for cart in carts:
            cart.total_price = total
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
            marshalqry["game_id"] = marshalGame
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
                marshaltd["game_id"] = marshalGame
                list_td.append(marshaltd)
            result.append({"cart": marshalqry, "transaction_detail": list_td})
        return result, 200

    @buyer_required
    def delete(self):
        claims = get_jwt_claims()
        carts = Carts.query.filter_by(user_id=claims["id"], status=True).all()

        if carts is None:
            return {'status': 'NOT_FOUND'}, 404

        for cart in carts:
            cartId = cart.id
            transDetail = TransactionDetails.query.filter_by(cart_id=cartId).all()
            for data in transDetail:
                db.session.delete(data)
            db.session.delete(cart)
        
        db.session.commit()
        return {"message": 'Deleted'}, 200


class CartHistoryResource(Resource):
    def options(self, id=None):
        return {'status': 'ok'}, 200

    @buyer_required
    def get(self):
        claims = get_jwt_claims()
        cart = Carts.query.filter_by(user_id=claims["id"])
        cart = cart.filter_by(status=False)
        cart = cart.order_by(desc(Carts.updated_at))
        cart = cart.all()
        result = []
        for qry in cart:
            game = Games.query.filter_by(id=qry.game_id).first()
            marshalGame = marshal(game, Games.response_fields)
            marshalqry = marshal(qry, Carts.response_fields)
            marshalqry["game_id"] = marshalGame
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
                marshaltd["game_id"] = marshalGame
                list_td.append(marshaltd)
            result.append(marshaltd)
            # result.append({"cart": marshalqry, "transaction_detail": list_td})
        return result, 200

class TransactionDetail(Resource):
    def options(self, id=None):
        return {'status': 'ok'}, 200

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
            marshalqry["game_id"] = marshalGame
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
                marshaltd["game_id"] = marshalGame
                result.append(marshaltd)
        return result, 200

    @buyer_required
    def delete(self):
        claims = get_jwt_claims()
        parser = reqparse.RequestParser()
        parser.add_argument("id", location="json", required=True)
        args = parser.parse_args()

        transDetail = TransactionDetails.query.get(args['id'])
        gameId = transDetail.game_id
        price = transDetail.price
        
        db.session.delete(transDetail)

        carts = Carts.query.filter_by(game_id=gameId, status=True).first()
        cartsActive = Carts.query.filter_by(status=True).all()

        for cart in cartsActive:
            cart.total_price -= price

        carts.total_price_item -= price
        if carts.total_price_item == 0:
            db.session.delete(carts)



        db.session.commit()
        return {"message": 'Deleted'}, 200

        # return marshal(self.get, TransactionDetails.response_fields), 200, {'Content-Type': 'application/json'}

class CartResume(Resource):
    def options(self, id=None):
        return {'status': 'ok'}, 200

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
            marshalqry["game_id"] = marshalGame
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
                marshaltd["game_id"] = marshalGame
                list_td.append(marshaltd)
            result.append(marshalqry)
        return result, 200

class CartPayment(Resource):
    def options(self, id=None):
        return {'status': 'ok'}, 200

    @buyer_required
    def put(self):
        parser = reqparse.RequestParser()
        parser.add_argument("payment", location="json", required=True)
        parser.add_argument("operator", location="json", required=True)
        args = parser.parse_args()

        claims = get_jwt_claims()
        user_id = claims['id']

        carts = Carts.query.filter_by(user_id=user_id).all()

        for cart in carts :
            cart.payment = args['payment']
            cart.operator = args['operator']
            cart.updated_at = datetime.now()

            db.session.commit()
        return marshal(carts, Carts.response_fields), 200, {'Content-Type': 'application/json'}

class CartCheckout(Resource):
    def options(self, id=None):
        return {'status': 'ok'}, 200

    @buyer_required
    def put(self):
        claims = get_jwt_claims()
        user_id = claims['id']

        carts = Carts.query.filter_by(user_id=user_id).all()

        for cart in carts :
            cart.status = False
            cart.updated_at = datetime.now()


            gameID = cart.game_id
            game = Games.query.get(gameID)

            tdetails = TransactionDetails.query.filter_by(cart_id=cart.id).all()
            for detail in tdetails:
                voucherQry = GameVouchers.query.get(detail.voucher_id)
                td = TransactionDetails.query.filter_by(cart_id=cart.id, voucher_id=voucherQry.id).first()
                game.sold += td.quantity

        db.session.commit()
        return marshal(carts, Carts.response_fields), 200, {'Content-Type': 'application/json'}

api.add_resource(TransactionDetail, "/detail")
api.add_resource(CartResume, "/resume")
api.add_resource(CartPayment, "/payment")
api.add_resource(CartResource, "", "/<int:id>")
api.add_resource(CartHistoryResource, "/history")
api.add_resource(CartCheckout, "/checkout")
