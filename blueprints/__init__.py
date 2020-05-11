
import hashlib
from datetime import timedelta
from functools import wraps
from flask_jwt_extended import JWTManager, verify_jwt_in_request, get_jwt_claims

import json
import config
import os
import jwt
from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager


app = Flask(__name__)
flaskenv = os.environ.get('FLASK_ENV', 'Production')
if flaskenv == "Production":
    app.config.from_object(config.ProductionConfig)
elif flaskenv == "Testing":
    app.config.from_object(config.TestingConfig)
else:
    app.config.from_object(config.DevelopmentConfig)

db = SQLAlchemy(app)
migrate = Migrate(app, db)
manager = Manager(app)
manager.add_command('db', MigrateCommand)

jwt = JWTManager(app)


def seller_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        claims = get_jwt_claims()
        if claims['status'] != 'seller':
            return {'status': 'FORBIDDEN', 'message': 'Internal only'}, 403
        else:
            return fn(*args, **kwargs)
    return wrapper


def buyer_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        claims = get_jwt_claims()
        if claims['status'] != 'buyer':
            return {'status': 'FORBIDDEN', 'message': 'Internal only'}, 403
        else:
            return fn(*args, **kwargs)
    return wrapper


@app.after_request
def after_request(response):
    try:
        requestData = request.get_json()
    except Exception as e:
        requestData = request.args.to_dict()
    if response.status_code == 200:
        app.logger.warning("REQUEST_LOG\t%s", json.dumps({
            'method': request.method,
            'code': response.status,
            'uri': request.full_path,
            'request': requestData,
            'response': json.loads(response.data.decode('utf-8'))
        })
        )
    else:
        app.logger.error("REQUEST_LOG\t%s", json.dumps({
            'method': request.method,
            'code': response.status,
            'uri': request.full_path,
            'request': requestData,
            'response': json.loads(response.data.decode('utf-8'))
        })
        )

    return response

from blueprints.auth import bp_auth
from blueprints.cart.resources import bp_cart
from blueprints.user.resources import bp_account
from blueprints.game.resources import bp_game, bp_game_public
from blueprints.seller.resources import bp_seller
from blueprints.buyer.resources import bp_buyer

app.register_blueprint(bp_auth, url_prefix='/login')
app.register_blueprint(bp_buyer, url_prefix='/users')
app.register_blueprint(bp_game_public, url_prefix='/public/game')
app.register_blueprint(bp_seller, url_prefix='/admin')
app.register_blueprint(bp_game, url_prefix='/admin/game')
app.register_blueprint(bp_cart, url_prefix='/cart')
app.register_blueprint(bp_account, url_prefix='/account')

db.create_all()
