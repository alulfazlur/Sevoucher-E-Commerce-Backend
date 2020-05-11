import json
import hashlib
import uuid
from blueprints import db, app, buyer_required, seller_required

from flask import Blueprint
from flask_restful import Resource, Api, reqparse, marshal, inputs
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required, get_jwt_claims
from sqlalchemy import desc

from .model import Buyers

bp_buyer = Blueprint('buyer', __name__)
api = Api(bp_buyer)


class BuyerResource(Resource):

    @buyer_required
    def get(self):
        claims = get_jwt_claims()
        userId = claims['id']
        qry = Buyers.query.filter_by(user_id=userId).first()
        if qry is not None:
            return marshal(qry, Buyers.response_fields), 200
        return {'status': 'NOT_FOUND'}, 404

    @buyer_required
    def post(self):
        claims = get_jwt_claims()
        userId = claims['id']

        parser = reqparse.RequestParser()
        parser.add_argument('name', location='json', required=True)
        parser.add_argument('email', location='json', required=True)
        parser.add_argument('address', location='json', required=True)
        parser.add_argument('phone', location='json', required=True)
        args = parser.parse_args()

        user = Buyers(args['name'], args['email'],
                      args['address'], args['phone'], userId)
        db.session.add(user)
        db.session.commit()

        app.logger.debug('DEBUG : %s', user)

        return marshal(user, Buyers.response_fields), 200, {'Content-Type': 'application/json'}

    @buyer_required
    def patch(self):
        parser = reqparse.RequestParser()
        parser.add_argument('name', location='json')
        parser.add_argument('email', location='json')
        parser.add_argument('address', location='json')
        parser.add_argument('phone', location='json')
        args = parser.parse_args()

        claims = get_jwt_claims()
        userId = claims['id']
        qry = Buyers.query.filter_by(user_id=userId).first()
        if qry is None:
            return {'status': 'NOT_FOUND'}, 404

        qry.name = args['name']
        qry.email = args['email']
        qry.address = args['address']
        qry.phone = args['phone']
        db.session.commit()

        return marshal(qry, Buyers.response_fields), 200, {'Content-Type': 'application/json'}


class BuyerList(Resource):

    @seller_required
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('p', type=int, location='args', default=1)
        parser.add_argument('rp', type=int, location='args', default=25)
        parser.add_argument('orderby', location='args',
                            help='invalid orderby value', choices=('id', 'user_id', 'name'))
        parser.add_argument('sort', location='args',
                            help='invalid sort value', choices=('desc', 'asc'))

        args = parser.parse_args()

        offset = (args['p'] * args['rp'] - args['rp'])

        qry = Buyers.query

        # Orderby
        if args['orderby'] is not None:
            if args['orderby'] == 'id':
                if args['sort'] == 'desc':
                    qry = qry.order_by(desc(Buyers.id))
                else:
                    qry = qry.order_by(Buyers.id)

            elif args['orderby'] == 'user_id':
                if args['sort'] == 'desc':
                    qry = qry.order_by(desc(Buyers.user_id))
                else:
                    qry = qry.order_by(Buyers.user_id)

            else:
                if args['sort'] == 'desc':
                    qry = qry.order_by(desc(Buyers.name))
                else:
                    qry = qry.order_by(Buyers.name)

        rows = []
        for row in qry.limit(args['rp']).offset(offset).all():
            rows.append(marshal(row, Buyers.response_fields))

        return rows, 200


api.add_resource(BuyerList, '/list')
api.add_resource(BuyerResource, '/me')
