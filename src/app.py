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
    db.session.add(user)  # crea a la transacción de db
    try:
        db.session.commit()
        return jsonify(user.serialize()), 201
    except Exception as err:
        db.sesion.rollback()
        return jsonify({"error": f"Error: {err.args}"})


@app.route("/users", methods=["GET"])
def get_all_users():
    try:
        users = User.query.all()

        # result_body = list(map(lambda item: item.serialize(), users))
        return jsonify({"users": [user.serialize() for user in users]}), 200

    except Exception as err:
        return jsonify({"message": f"Error: {err.args}"}), 500


@app.route("/users/<string:user_name>", methods=["DELETE"])
def delete_user(user_name):
    user = User.query.filter_by(name=user_name).first()

    if user is None:
        # raise APIException("User not fount", status_code=404)
        return jsonify({"message": "User not found"}), 404

    db.session.delete(user)
    db.session.commit()

    return jsonify({}), 204


@app.route("/users/<string:user_name>", methods=["GET"])
def read_user(user_name):

    user = User.query.filter_by(name=user_name.lower()).first()
    if user is None:
        return jsonify({"message": "User not found"}), 404

    return jsonify(user.serialize_with_items())


@app.route("/todos/<string:user_name>", methods=["POST"])
def create_user_todo(user_name):
    body = request.get_json(silent=True) or {}
    label = body.get("label")
    is_done = body.get("is_done", False)

    if not isinstance(label, str) or label.strip() == '':
        raise APIException(
            "label required an must be a string", status_code=400)

    if not isinstance(is_done, bool):
        return jsonify({"message": "is_done must be a bolean"}), 400

    user = User.query.filter_by(name=user_name.lower()).first()
    if user is None:
        return jsonify({"message": "User not found"}), 404

    todo = Todo(label=label.strip(), is_done=is_done, user_id=user.id)
    db.session.add(todo)
    try:
        db.session.commit()
        return jsonify(todo.serialize()), 201
    except Exception as err:
        return jsonify({"message": f"Error: {err.args}"}), 500


@app.route("/todos/<int:todo_id>", methods=["PUT"])
def update_user_todo(todo_id):
    body = request.get_json(silent=True) or {}

    todo = Todo.query.get(todo_id)
    if todo is None:
        return jsonify({"message": "Todo not found"}), 404

    if 'label' in body and body['label'] is not None:
        if not isinstance(body["label"], str) or body["label"].strip() == "":
            raise APIException(
                "label required an must be a string", status_code=400)
        todo.label = body["label"].strip()

    if 'is_done' in body and body['is_done'] is not None:
        if not isinstance(body["is_done"], bool):
            return jsonify({"message": "is_done must be a bolean"}), 400
        todo.is_done = body["is_done"]

    try:
        db.session.commit()
        return jsonify(todo.serialize()), 200
    except Exception as err:
        return jsonify({"message": f"Error: {err.args}"}), 500


@app.route("/todos/<int:todo_id>", methods=["DELETE"])
def delete_task(todo_id):
    todo = Todo.query.get(todo_id)

    if todo is None:
        return jsonify({"message": "Todo not found"}), 404

    db.session.delete(todo)
    # db.session.commit()

    return jsonify({}), 204


    # this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)

    """
        2.- lanzar a producción (render.com)
        3.- probar al azar con uno hecho de los estudiante
    """
