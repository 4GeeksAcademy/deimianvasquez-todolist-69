"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Todo
# from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace(
        "postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object


@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints


@app.route('/')
def sitemap():
    return generate_sitemap(app)


@app.route('/users/<string:user_name>', methods=['POST'])
def create_user(user_name):
    # select * from user where name="deimian"
    existing_user = User.query.filter_by(name=user_name.lower()).first()
    if existing_user is not None:
        return jsonify("user already exists"), 400

    user = User(name=user_name)  # name --> deimian
    db.session.add(user)
    try:
        db.session.commit()
        return jsonify(user.serialize()), 201
    except Exception as err:
        db.sesion.rollback()
        return jsonify({"error": f"Error: {err.args}"})


@app.route("/users", methods=["GET"])
def get_all_users():
    users = User.query.all()
    print(users)
    # result_body = list(map(lambda item: item.serialize(), users))
    return jsonify({"users": [user.serialize() for user in users]}), 200


# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)

    """
        1.- terminar los endpoints
        2.- lanzar a producción (render.com)
        3.- probar al azar con uno hecho de los estudiante
    """
