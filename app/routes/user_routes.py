from flask import Blueprint, jsonify, make_response, redirect, render_template, request, current_app
from pydantic import ValidationError
from app import db
from bson import ObjectId
from app.models.user import *
from app.decorators import token_required
from datetime import timezone, timedelta, datetime
import jwt

user_bp = Blueprint('user_bp', __name__)

# Rota de Autenticação
@user_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template("login.html")
    
    try:
        username = request.form.get("username")
        password = request.form.get("password")
        
        if not username or not password:
            return render_template("login.html", error="Preencha os campos")
        
        user = db.users.find_one({
            "username": username, 
            "password": password
            })
        
    except Exception:
        return render_template("login.html", error="Erro interno"), 500

    if user:
        token = jwt.encode( 
            {
                "user_id": str(user["_id"]),
                "exp": datetime.now(timezone.utc) + timedelta(minutes = 30)
            },
            current_app.config['SECRET_KEY'],
            algorithm='HS256'
        )
        response = make_response(redirect("/dashboard"))
        response.set_cookie("token", token, httponly=True, samesite="Strict")
        return response
    return render_template("login.html", error="Credenciais inválidas"), 401

# Create an user
@user_bp.route("/usuarios", methods=["POST"])
def create_user():
    user_data = request.get_json()

    if not isinstance(user_data, dict): #verify if body requisition exists
        return jsonify({"error": "Body inválido"}), 400
    
    user_data.pop("_id", None)

    try:
        user = User(**user_data)
    except ValidationError as e:
        return jsonify({"error":e.errors()}), 400

    if db.users.find_one({"username": user.username}): #verify duplicates
            return jsonify({"error": "Usuário ja existe"}), 409
    
    user_result = db.users.insert_one(user.model_dump())
    return jsonify({"message":"Rota de criação de usuarios",
                    "id": str(user_result.inserted_id)}), 201

# List all users from DB
@user_bp.route("/usuarios", methods=["GET"])
@token_required
def get_users(token):
    users_cursor = db.users.find({},{"password": 0})
    users_list = []
    for user in users_cursor:
        user["_id"] = str(user["_id"])
        users_list.append(UserResponse(**user).model_dump(by_alias=True))
    return jsonify(users_list)

# Delete existing user
@user_bp.route("/usuarios/<string:user_id>", methods=["DELETE"])
@token_required
def delete_user_from_db(token, user_id):
    try:
        oid = ObjectId(user_id)
    except Exception:
        return jsonify({"error": "id do usuário inválido"}), 400
    
    delete_user = db.users.delete_one({"_id": oid})

    if delete_user.deleted_count == 0:
        return jsonify({"error": "Usuário não foi encontrado"}), 404

    return "", 204