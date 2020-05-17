import json
import hashlib
import uuid
from blueprints import db, app, buyer_required, seller_required

from flask import Blueprint
from flask_restful import Resource, Api, reqparse, marshal, inputs
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required, get_jwt_claims
from sqlalchemy import desc

from .model import Sellers

bp_seller = Blueprint('seller', __name__)
api = Api(bp_seller)


class SellerResourceSignUp(Resource):
    def options(self, id=None):
        return {'status': 'ok'}, 200

    def post(self):
        parser = reqparse.RequestParser()

        parser.add_argument('username', location='json', required=True)
        parser.add_argument('password', location='json', required=True)
        parser.add_argument('name', location='json', required=True)
        parser.add_argument('email', location='json', required=True)
        # parser.add_argument('avatar', location='json')
        parser.add_argument('address', location='json', required=True)
        parser.add_argument('phone', location='json', required=True)

        args = parser.parse_args()

        salt = uuid.uuid4().hex
        encoded = ('%s%s' % (args['password'], salt)).encode('utf-8')
        hash_pass = hashlib.sha512(encoded).hexdigest()

        user = Sellers(args['username'], hash_pass, args['name'], args['email'],
                       #    args['avatar'],
                       args['address'], args['phone'], args['status'], salt)
        db.session.add(user)
        db.session.commit()

        app.logger.debug('DEBUG : %s', user)

        return marshal(user, Sellers.response_fields), 200, {'Content-Type': 'application/json'}


class SellerResource(Resource):
    def options(self, id=None):
        return {'status': 'ok'}, 200

    @seller_required
    def get(self):
        claims = get_jwt_claims()
        userId = claims['id']
        qry = Sellers.query.filter_by(id=userId).first()
        if qry is None:
            return {'status': 'NOT_FOUND'}, 404
        if qry is not None:
            return marshal(qry, Sellers.response_fields), 200
        return {'status': 'NOT_FOUND'}, 404

    @seller_required
    def put(self):
        parser = reqparse.RequestParser()
        parser.add_argument('name', location='json')
        parser.add_argument('email', location='json')
        parser.add_argument('address', location='json')
        parser.add_argument('phone', location='json')

        args = parser.parse_args()

        claims = get_jwt_claims()
        userId = claims['id']
        qry = Sellers.query.filter_by(id=userId).first()
        if qry is None:
            return {'status': 'NOT_FOUND'}, 404

        if args['name'] is not None:
            qry.name = args['name']
        if args['email'] is not None:
            qry.email = args['email']
        if args['address'] is not None:
            qry.address = args['address']
        if args['phone'] is not None:
            qry.phone = args['phone']
        # if args['avatar'] is not None:
            # qry.name = args['avatar']
        db.session.commit()

        return marshal(qry, Sellers.response_fields), 200, {'Content-Type': 'application/json'}


class SellerList(Resource):
    def options(self, id=None):
        return {'status': 'ok'}, 200

    @seller_required
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('p', type=int, location='args', default=1)
        parser.add_argument('rp', type=int, location='args', default=25)
        parser.add_argument('orderby', location='args',
                            help='invalid orderby value', choices=('id', 'name'))
        parser.add_argument('sort', location='args',
                            help='invalid sort value', choices=('desc', 'asc'))

        args = parser.parse_args()

        offset = (args['p'] * args['rp'] - args['rp'])

        qry = Sellers.query

        # Orderby
        if args['orderby'] is not None:
            if args['orderby'] == 'id':
                if args['sort'] == 'desc':
                    qry = qry.order_by(desc(Sellers.id))
                else:
                    qry = qry.order_by(Sellers.id)

            elif args['orderby'] == 'id':
                if args['sort'] == 'desc':
                    qry = qry.order_by(desc(Sellers.id))
                else:
                    qry = qry.order_by(Sellers.id)

            else:
                if args['sort'] == 'desc':
                    qry = qry.order_by(desc(Sellers.name))
                else:
                    qry = qry.order_by(Sellers.name)

        rows = []
        for row in qry.limit(args['rp']).offset(offset).all():
            rows.append(marshal(row, Sellers.response_fields))

        return rows, 200


api.add_resource(SellerList, '/list')
api.add_resource(SellerResourceSignUp, '')
api.add_resource(SellerResource, '/me')
