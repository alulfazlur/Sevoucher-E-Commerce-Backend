import json
import hashlib
import uuid
from blueprints import db, app, buyer_required, seller_required

from flask import Blueprint
from flask_restful import Resource, Api, reqparse, marshal, inputs
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required, get_jwt_claims
from sqlalchemy import desc

from .model import Games, GameVouchers

bp_game = Blueprint('game', __name__)
api = Api(bp_game)

bp_game_public = Blueprint('public game', __name__)
api_public = Api(bp_game_public)

bp_voucher_public = Blueprint('public voucher', __name__)
api_public_voucher = Api(bp_voucher_public)

class GameResource(Resource):
    def options(self, id=None):
        return {'status': 'ok'}, 200

    @seller_required
    def post(self):
        claims = get_jwt_claims()
        parser = reqparse.RequestParser()

        parser.add_argument('name', location='json', required=True)
        parser.add_argument('tile', location='json', required=True)
        parser.add_argument('banner', location='json', required=True)
        parser.add_argument('publisher', location='json', required=True)
        parser.add_argument('description', location='json', required=True)
        parser.add_argument('category', location='json',
                            required=True, choices=('mobile', 'pc', 'credits'))
        parser.add_argument('gplay', location='json')
        parser.add_argument('appstore', location='json')
        parser.add_argument('website', location='json')
        parser.add_argument('community', location='json')
        parser.add_argument('promo', location='json', type=bool)
        parser.add_argument('discount', location='json')
        # parser.add_argument('sold', location='json')

        args = parser.parse_args()
        game = Games(args['name'], args['tile'], args['banner'], args['publisher'],
                     args['description'], args['category'], args['gplay'],
                     args['appstore'], args['website'], args['community'],
                     args['promo'], args['discount']  # , args['sold']
                     )
        db.session.add(game)
        db.session.commit()

        app.logger.debug('DEBUG : %s', game)

        return marshal(game, Games.response_fields), 200, {'Content-Type': 'application/json'}

    @seller_required
    def put(self):
        parser = reqparse.RequestParser()
        parser.add_argument('name', location='json', required=True)
        parser.add_argument('newName', location='json')
        parser.add_argument('tile', location='json')
        parser.add_argument('banner', location='json')
        parser.add_argument('publisher', location='json')
        parser.add_argument('description', location='json')
        parser.add_argument('category', location='json', choices=('mobile', 'pc', 'credits'))
        parser.add_argument('gplay', location='json')
        parser.add_argument('appstore', location='json')
        parser.add_argument('website', location='json')
        parser.add_argument('community', location='json')
        parser.add_argument('promo', location='json', type=bool)
        parser.add_argument('discount', location='json')
        parser.add_argument('sold', location='json')

        args = parser.parse_args()

        qry = Games.query.filter_by(
            name=args['name']).first()
        if qry is None:
            return {'status': 'NOT_FOUND'}, 404
        
        if args['newName'] is not None:
            qry.name = args['newName']
        if args['tile'] is not None:
            qry.tile = args['tile']
        if args['banner'] is not None:
            qry.banner = args['banner']
        if args['publisher'] is not None:
            qry.publisher = args['publisher']
        if args['description'] is not None:
            qry.description = args['description']
        if args['category'] is not None:
            qry.category = args['category']
        if args['gplay'] is not None:
            qry.gplay = args['gplay']
        if args['appstore'] is not None:
            qry.appstore = args['appstore']
        if args['website'] is not None:
            qry.website = args['website']
        if args['community'] is not None:
            qry.community = args['community']
        if args['promo'] is not None:
            qry.promo = args['promo']
        if args['discount'] is not None:
            qry.discount = args['discount']
        if args['sold'] is not None:
            qry.sold = args['sold']

        db.session.commit()
        return marshal(qry, Games.response_fields), 200, {'Content-Type': 'application/json'}

    @seller_required
    def delete(self):
        parser = reqparse.RequestParser()
        parser.add_argument('name', location='args', required=True)
        args = parser.parse_args()

        qry = Games.query.filter_by(
            name=args['name']).first()
        if qry is None:
            return {'status': 'NOT_FOUND'}, 404

        db.session.delete(qry)
        db.session.commit()

        return {'status': 'DELETED'}, 200


class GameDetailResource(Resource):
    def options(self, id=None):
        return {'status': 'ok'}, 200

    def get(self):
        parser = reqparse.RequestParser()
        # parser.add_argument('name', location='args', required=True)
        args = parser.parse_args()

        qry = Games.query.all()
        # .filter_by(
        #     name=args['name']).first()
        if qry is not None:
            return marshal(qry, Games.response_fields), 200
        return {'status': 'NOT_FOUND'}, 404

# ============================================= Voucher ==============================================


class GameVoucherResource(Resource):
    def options(self, id=None):
        return {'status': 'ok'}, 200

    @seller_required
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('name', location='json', required=True)
        parser.add_argument('voucher', location='json', required=True)
        parser.add_argument('price', location='json', type=int, required=True)
        args = parser.parse_args()

        qry = Games.query.filter_by(
            name=args['name']).first()
        if qry is None:
            return {'status': 'NOT_FOUND'}, 404

        game_id = qry.id

        voucher = GameVouchers(game_id, args['voucher'], args['price'])
        db.session.add(voucher)
        db.session.commit()

        app.logger.debug('DEBUG : %s', voucher)

        return marshal(voucher, GameVouchers.response_fields), 200, {'Content-Type': 'application/json'}

    @seller_required
    def put(self):
        parser = reqparse.RequestParser()
        parser.add_argument('gameName', location='json', required=True)
        parser.add_argument('voucher', location='json', required=True)
        parser.add_argument('newVoucher', location='json')
        parser.add_argument('price', location='json')
        args = parser.parse_args()

        gameName = Games.query.filter_by(name=args['gameName']).first()
        gameId = gameName.id
        qry = GameVouchers.query.filter_by(game_id=gameId, voucher=args['voucher']).first()
        if qry is None:
            return {'status': 'NOT_FOUND'}, 404

        if args['newVoucher'] is not None:
            qry.newVoucher = args['newVoucher']
        if args['price'] is not None:
            qry.price = args['price']
            
        db.session.commit()

        return marshal(qry, GameVouchers.response_fields), 200, {'Content-Type': 'application/json'}

    @seller_required
    def delete(self):
        parser = reqparse.RequestParser()
        parser.add_argument('gameName', location='args', required=True)
        parser.add_argument('voucher', location='args', required=True)
        args = parser.parse_args()

        game = Games.query.filter_by(name=args['gameName']).first()
        if game is None:
            return {'status': 'NOT_FOUND'}, 404
        game_id = game.id

        voucher = GameVouchers.query.filter_by(game_id=game_id, voucher=args['voucher'] ).first()

        db.session.delete(voucher)
        db.session.commit()

        return {'status': 'DELETED'}, 200

class GameVoucherResourceGet(Resource):
    def options(self, id=None):
        return {'status': 'ok'}, 200

    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('gameName', location='args', required=True)
        # parser.add_argument('voucher', location='args')
        args = parser.parse_args()

        game = Games.query.filter_by(name=args['gameName']).first()
        if game is None:
            return {'status': 'GAME_NOT_FOUND'}, 404

        game_id = game.id
        voucher = GameVouchers.query.filter_by(game_id=game_id).all()

        if voucher is None:
            return {'status': 'VOUCHER_NOT_FOUND'}, 404
        else : 
            return marshal(voucher, GameVouchers.response_fields), 200, {'Content-Type': 'application/json'}

class GameVoucherListResource(Resource):
    def options(self, id=None):
        return {'status': 'ok'}, 200

    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('p', type=int, location='args', default=1)
        parser.add_argument('rp', type=int, location='args', default=25)
        parser.add_argument('game_id', location='args',
                            help='invalid game_id')
        parser.add_argument('orderby', location='args',
                            help='invalid orderby value', choices=('id', 'game_id'))
        parser.add_argument('sort', location='args',
                            help='invalid sort value', choices=('desc', 'asc'))

        args = parser.parse_args()

        offset = (args['p'] * args['rp'] - args['rp'])

        qry = GameVouchers.query

        # Filter game_id
        if args['game_id'] is not None:
            qry = qry.filter_by(game_id=args['game_id'])

        # Orderby
        if args['orderby'] is not None:
            if args['orderby'] == 'id':
                if args['sort'] == 'desc':
                    qry = qry.order_by(desc(GameVouchers.id))
                else:
                    qry = qry.order_by(GameVouchers.id)

            elif args['orderby'] == 'game_id':
                if args['sort'] == 'desc':
                    qry = qry.order_by(desc(GameVouchers.game_id))
                else:
                    qry = qry.order_by(GameVouchers.game_id)

        rows = []
        for row in qry.limit(args['rp']).offset(offset).all():
            rows.append(marshal(row, GameVouchers.response_fields))

        return rows, 200


api.add_resource(GameResource, '')
api.add_resource(GameVoucherResource, '/voucher')

api_public.add_resource(GameDetailResource, '')

api_public_voucher.add_resource(GameVoucherResourceGet, '')
api_public_voucher.add_resource(GameVoucherListResource, '/list')
