from flask import Blueprint, jsonify, request, current_app
from app.models.user import LoginPayload
from pydantic import ValidationError
from app import db
from bson import ObjectId
from app.models.products import *
from app.decorators import token_required
from datetime import timezone, timedelta, datetime
import jwt

main_bp = Blueprint('main_bp', __name__)

# Rota de Autenticação
@main_bp.route('/login', methods=['POST'])
def login():
    try:
        raw_data = request.get_json()
        user_data = LoginPayload(**raw_data)

    except ValidationError as e:
        return jsonify({"error": e.errors()}), 400
    except Exception as e:
        jsonify({'error': 'Erro durante a requisição de dado '}), 500

    try:
        if user_data.username == "admin" and user_data.password == "123":
            token = jwt.encode(
                {
                    "user_id": user_data.username,
                    "exp": datetime.now(timezone.utc) + timedelta(minutes = 30)
                },
                current_app.config['SECRET_KEY'],
                algorithm='HS256'
            )
            return jsonify({'access_token': token,
                            "message":f"Rota de autenticação do usuario {user_data.model_dump_json()}"}), 200
    except UnboundLocalError as e:
        return jsonify({"error":f"Nenhum dado foi inserido na requisição: {e}"})

# Rota de produtos
@main_bp.route('/products', methods=['GET'])
def get_products():
    products_cursor = db.products.find({})
    products_list = [
        ProductDBModel(**product).model_dump(by_alias=True, exclude_none=True) for product in products_cursor
        ]
    return jsonify(products_list)

# Cria um produto se fornecer o token
@main_bp.route('/product', methods=['POST'])
@token_required
def create_product(token):
    try:
        product = Product(**request.get_json())
    except ValidationError as e:
        return jsonify({"error":e.errors()})
    
    result = db.products.insert_one(product.model_dump())
    return jsonify({"message":"Rota de criação de produtos",
                    "id": str(result.inserted_id)}), 201

@main_bp.route('/product/<string:product_id>', methods=['GET'])
def get_product_by_id(product_id):
    try:
        oid = ObjectId(product_id)
    except Exception as e:
        return jsonify({"error":f"Erro ao transformar o {product_id} em ObjectId: {e}"})
    
    product = db.products.find_one({'_id':oid})

    if product:
        product_model = ProductDBModel(**product).model_dump(by_alias=True, exclude_none=True)
        return jsonify(product_model)
    else:
        return jsonify({"error":f"Produto com o {product_id} - Não encontrado !"})

@main_bp.route('/product/<string:product_id>', methods=['PUT'])
@token_required
def update_product(token, product_id):
    try:
        oid = ObjectId(product_id)
        update_data = UpdateProduct(**request.get_json())
    except ValidationError as e:
        return jsonify({"error": e.errors()})
    
    update_result = db.products.update_one(
        {"_id": oid},
        {"$set": update_data.model_dump(exclude_unset = True)}
    )
    if update_result.matched_count == 0:
        return jsonify({"error": "Produto não Encontrado"}), 404
    
    update_product = db.products.find_one({"_id": oid})
    return jsonify(ProductDBModel(**update_product).model_dump(by_alias=True, exclude=None))

@main_bp.route('/product/<string:product_id>', methods=['DELETE'])
@token_required
def delete_product(token, product_id):
    try:
        oid = ObjectId(product_id)
    except Exception:
        return jsonify({"error": "id do produto inválido"}), 400
    
    delete_product = db.products.delete_one({"_id": oid})

    if delete_product.deleted_count == 0:
        return jsonify({"error": "Produto não foi encontrado"}), 404
    
    return "", 204

@main_bp.route('/sales/upload', methods=['POST'])
def upload_sales():
    return jsonify({"message":"Rota de upload do arquivo de vendas"})

@main_bp.route('/')
def index():
    return jsonify({"message":"Bem vindo ao Stiles"})
