import json
import hashlib
import uuid
from blueprints import db, app, buyer_required, seller_required

from flask import Blueprint
from flask_restful import Resource, Api, reqparse, marshal, inputs
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required, get_jwt_claims
from sqlalchemy import desc

from .model import Users

bp_account = Blueprint('account', __name__)
api = Api(bp_account)


class UserResource(Resource):

    def post(self):
        parser = reqparse.RequestParser()

        parser.add_argument('username', location='json', required=True)
        parser.add_argument('password', location='json', required=True)
        parser.add_argument('status', location='json',
                            required=True, choices=('seller', 'buyer'))
        args = parser.parse_args()

        salt = uuid.uuid4().hex
        encoded = ('%s%s' % (args['password'], salt)).encode('utf-8')
        hash_pass = hashlib.sha512(encoded).hexdigest()

        user = Users(args['username'], hash_pass, args['status'], salt)
        db.session.add(user)
        db.session.commit()

        app.logger.debug('DEBUG : %s', user)

        return marshal(user, Users.response_fields), 200, {'Content-Type': 'application/json'}

    def get(self, id):
        qry = Users.query.get(id)
        if qry is not None:
            return marshal(qry, Users.response_fields), 200
        return {'status': 'NOT_FOUND'}, 404

    @seller_required
    def patch(self, id):
        parser = reqparse.RequestParser()
        parser.add_argument('username', location='json')
        parser.add_argument('password', location='json')
        parser.add_argument('status', location='json',
                            choices=('seller', 'buyer'))
        args = parser.parse_args()

        qry = Users.query.get(id)
        if qry is None:
            return {'status': 'NOT_FOUND'}, 404

        qry.username = args['username']
        qry.password = args['password']
        qry.status = args['status']
        db.session.commit()

        return marshal(qry, Users.response_fields), 200, {'Content-Type': 'application/json'}

    @seller_required
    def delete(self, id):
        qry = Users.query.get(id)
        if qry is None:
            return {'status': 'NOT_FOUND'}, 404

        db.session.delete(qry)
        db.session.commit()

        return {'status': 'DELETED'}, 200


class UserList(Resource):
    @seller_required
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('p', type=int, location='args', default=1)
        parser.add_argument('rp', type=int, location='args', default=25)
        parser.add_argument('status', location='args', help='invalid status')
        parser.add_argument('orderby', location='args',
                            help='invalid orderby value', choices=('id', 'status'))
        parser.add_argument('sort', location='args',
                            help='invalid sort value', choices=('desc', 'asc'))

        args = parser.parse_args()

        offset = (args['p'] * args['rp'] - args['rp'])

        qry = Users.query

        # Filter status
        if args['status'] is not None:
            if args['status'].lower() == 'seller':
                qry = qry.filter_by(status="seller")
            else:
                qry = qry.filter_by(status="buyer")

        # Orderby
        if args['orderby'] is not None:
            if args['orderby'] == 'id':
                if args['sort'] == 'desc':
                    qry = qry.order_by(desc(Users.id))
                else:
                    qry = qry.order_by(Users.id)

            elif args['orderby'] == 'status':
                if args['sort'] == 'desc':
                    qry = qry.order_by(desc(Users.status))
                else:
                    qry = qry.order_by(Users.status)

        rows = []
        for row in qry.limit(args['rp']).offset(offset).all():
            rows.append(marshal(row, Users.response_fields))

        return rows, 200


api.add_resource(UserList, '/list')
api.add_resource(UserResource, '', '/<id>')
