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
    def patch(self, id):
        parser = reqparse.RequestParser()
        parser.add_argument('name', location='json')
        parser.add_argument('tile', location='json')
        parser.add_argument('banner', location='json')
        parser.add_argument('publisher', location='json')
        parser.add_argument('description', location='json')
        parser.add_argument('category', location='json', choices=('mobile', 'pc', 'credits'))
        parser.add_argument('gplay', location='json')
        parser.add_argument('appstore', location='json')
        parser.add_argument('website', location='json')
        parser.add_argument('community', location='json')
        parser.add_argument('promo', location='json')
        parser.add_argument('discount', location='json')
        parser.add_argument('sold', location='json')

        args = parser.parse_args()

        qry = Games.query.get(id).first()
        if qry is None:
            return {'status': 'NOT_FOUND'}, 404

        qry.name = args['name']
        qry.tile = args['tile']
        qry.banner = args['banner']
        qry.publisher = args['publisher']
        qry.description = args['description']
        qry.category = args['category']
        qry.gplay = args['gplay']
        qry.appstore = args['appstore']
        qry.website = args['website']
        qry.community = args['community']
        qry.promo = args['promo']
        qry.discount = args['discount']
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

    def get(self, id):
        qry = Games.query.get(id=id).first()
        if qry is not None:
            return marshal(qry, Games.response_fields), 200
        return {'status': 'NOT_FOUND'}, 404


class GameFilterResource(Resource):
    def options(self, id=None):
        return {'status': 'ok'}, 200

    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('p', type=int, location='args', default=1)
        parser.add_argument('rp', type=int, location='args', default=25)
        parser.add_argument('publisher', location='args',
                            help='invalid publisher')
        parser.add_argument('category', location='args',
                            help='invalid category', choices=('mobile', 'pc', 'credits'))
        parser.add_argument('promo', location='args',
                            help='invalid promo')
        parser.add_argument('orderby', location='args',
                            help='invalid orderby value', choices=('id', 'name', 'publisher'))
        parser.add_argument('sort', location='args',
                            help='invalid sort value', choices=('desc', 'asc'))

        args = parser.parse_args()
        offset = (args['p'] * args['rp'] - args['rp'])

        qry = Games.query

        # Filter publisher
        if args['publisher'] is not None:
            qry = qry.filter_by(publisher=args['publisher'])

        # Filter category
        if args['category'] is not None:
            qry = qry.filter_by(category=args['category'])

        # Orderby
        if args['orderby'] is not None:
            if args['orderby'] == 'id':
                if args['sort'] == 'desc':
                    qry = qry.order_by(desc(Games.id))
                else:
                    qry = qry.order_by(Games.id)

            elif args['orderby'] == 'name':
                if args['sort'] == 'desc':
                    qry = qry.order_by(desc(Games.name))
                else:
                    qry = qry.order_by(Games.name)

            elif args['orderby'] == 'publisher':
                if args['sort'] == 'desc':
                    qry = qry.order_by(desc(Games.publisher))
                else:
                    qry = qry.order_by(Games.publisher)

        rows = []
        for row in qry.limit(args['rp']).offset(offset).all():
            rows.append(marshal(row, Games.response_fields))

        return rows, 200


class GamePromoResource(Resource):
    def options(self, id=None):
        return {'status': 'ok'}, 200

    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('p', type=int, location='args', default=1)
        parser.add_argument('rp', type=int, location='args', default=25)
        parser.add_argument('orderby', location='args',
                            help='invalid orderby value', choices=('id', 'name', 'publisher'))
        parser.add_argument('sort', location='args',
                            help='invalid sort value', choices=('desc', 'asc'))

        args = parser.parse_args()
        offset = (args['p']*args['rp'])-args['rp']

        qry = Games.query.filter_by(promo=True)

        # Orderby
        if args['orderby'] is not None:
            if args['orderby'] == 'id':
                if args['sort'] == 'desc':
                    qry = qry.order_by(desc(Games.id))
                else:
                    qry = qry.order_by(Games.id)

            elif args['orderby'] == 'name':
                if args['sort'] == 'desc':
                    qry = qry.order_by(desc(Games.name))
                else:
                    qry = qry.order_by(Games.name)

            elif args['orderby'] == 'publisher':
                if args['sort'] == 'desc':
                    qry = qry.order_by(desc(Games.publisher))
                else:
                    qry = qry.order_by(Games.publisher)

        rows = []
        for row in qry.limit(args['rp']).offset(offset).all():
            rows.append(marshal(row, Games.response_fields))

        return rows, 200


class GameSearchResource(Resource):
    def options(self, id=None):
        return {'status': 'ok'}, 200

    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('p', type=int, location='args', default=1)
        parser.add_argument('rp', type=int, location='args', default=25)
        parser.add_argument("q", location="args")
        parser.add_argument('orderby', location='args',
                            help='invalid orderby value', choices=('id', 'name', 'publisher'))
        parser.add_argument('sort', location='args',
                            help='invalid sort value', choices=('desc', 'asc'))

        args = parser.parse_args()
        offset = (args['p']*args['rp'])-args['rp']

        if args['keyword'] is not None:
            qry = Games.query.filter(Games.name.like("%"+args['keyword']+"%") |
                                     Games.category.like("%"+args['keyword']+"%") |
                                     Games.publisher.like("%"+args['keyword']+"%") |
                                     Games.description.like("%"+args['keyword']+"%"))

        # Orderby
        if args['orderby'] is not None:
            if args['orderby'] == 'id':
                if args['sort'] == 'desc':
                    qry = qry.order_by(desc(Games.id))
                else:
                    qry = qry.order_by(Games.id)

            elif args['orderby'] == 'name':
                if args['sort'] == 'desc':
                    qry = qry.order_by(desc(Games.name))
                else:
                    qry = qry.order_by(Games.name)

            elif args['orderby'] == 'publisher':
                if args['sort'] == 'desc':
                    qry = qry.order_by(desc(Games.publisher))
                else:
                    qry = qry.order_by(Games.publisher)

        rows = []
        for row in qry.limit(args['rp']).offset(offset).all():
            rows.append(marshal(row, Games.response_fields))

        return rows, 200


class GamePopularResource(Resource):
    def options(self, id=None):
        return {'status': 'ok'}, 200

    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('p', type=int, location='args', default=1)
        parser.add_argument('rp', type=int, location='args', default=25)

        args = parser.parse_args()
        offset = (args['p']*args['rp'])-args['rp']

        qry = Games.query.order_by(desc(Games.sold))

        rows = []
        for row in qry.limit(args['rp']).offset(offset).all():
            rows.append(marshal(row, Games.response_fields))

        return rows, 200

# ============================================= Voucher ==============================================


class GameVoucherResource(Resource):
    def options(self, id=None):
        return {'status': 'ok'}, 200

    def get(self, game):
        gameName = Games.query.filter_by(
            name=game.lower().replace('-', ' ')).first()
        gameId = gameName.id
        qry = GameVouchers.query.filter_by(game_id=gameId).first()
        if qry is not None:
            return marshal(qry, GameVouchers.response_fields), 200
        return {'status': 'NOT_FOUND'}, 404

    @seller_required
    def post(self, game):
        parser = reqparse.RequestParser()
        parser.add_argument('voucher', location='json', required=True)
        parser.add_argument('price', location='json', required=True)

        gameName = Games.query.filter_by(
            name=game.lower().replace('-', ' ')).first()
        if gameName is None:
            return {"message": "Game Not Available"}, 404

        game_id = gameName.id

        args = parser.parse_args()
        voucher = GameVouchers(game_id, args['voucher'], args['price'])
        db.session.add(voucher)
        db.session.commit()

        app.logger.debug('DEBUG : %s', voucher)

        return marshal(voucher, GameVouchers.response_fields), 200, {'Content-Type': 'application/json'}

    @seller_required
    def patch(self, game):
        parser = reqparse.RequestParser()
        parser.add_argument('voucher', location='json', required=True)
        parser.add_argument('price', location='json', required=True)
        args = parser.parse_args()

        gameName = Games.query.filter_by(
            name=game.lower().replace('-', ' ')).first()
        gameId = gameName.id
        qry = GameVouchers.query.filter_by(game_id=gameId).first()
        if qry is None:
            return {'status': 'NOT_FOUND'}, 404

        qry.voucher = args['voucher']
        qry.price = args['price']

        db.session.commit()

        return marshal(qry, GameVouchers.response_fields), 200, {'Content-Type': 'application/json'}

    @seller_required
    def delete(self, game):
        gameName = Games.query.filter_by(
            name=game.lower().replace('-', ' ')).first()
        gameId = gameName.id
        qry = GameVouchers.query.filter_by(game_id=gameId).first()
        if qry is None:
            return {'status': 'NOT_FOUND'}, 404

        db.session.delete(qry)
        db.session.commit()

        return {'status': 'DELETED'}, 200


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

api_public.add_resource(GameDetailResource, '/<id>')
api_public.add_resource(GameFilterResource, '')
api_public.add_resource(GamePromoResource, '/promo')
api_public.add_resource(GameSearchResource, '/search')
api_public.add_resource(GamePopularResource, '/popular')

api.add_resource(GameVoucherResource, '/<game>/voucher')
api.add_resource(GameVoucherListResource, '/voucher')
