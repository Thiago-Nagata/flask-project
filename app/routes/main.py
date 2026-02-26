from flask import Blueprint, jsonify, request
from pydantic import ValidationError
from app import db
from bson import ObjectId
from app.models.products import *
from app.models.sale import Sale
from app.decorators import token_required
import os
import io
import csv

main_bp = Blueprint('main_bp', __name__)

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
@token_required
def upload_sales(token):
    if 'file' not in request.files:
        return jsonify({"error":"Nenhum arquivo foi encontrado"}), 400
    
    file = request.files['file']

    if file.filename == '':
        return jsonify({"error": "Nenhum arquivo selecionado"}), 400
    
    if file and file.filename.endswith('.csv'):
        csv_stream = io.StringIO(file.stream.read().decode('UTF-8'), newline=None)
        csv_reader = csv.DictReader(csv_stream)

        sales_to_insert = []
        error = []

        for row_num, row in enumerate(csv_reader, 1):
            try:
                sale_data = Sale(**row)

                sales_to_insert.append(sale_data.model_dump())
            except ValidationError as e:
                error.append(f'Linha {row_num} com dados inválidos')
            except Exception:
                error.append(f'Linha {row_num} com erro inesperado nos dados')

        if sales_to_insert:
            try:
                db.sales.insert_many(sales_to_insert)
            except Exception as e:
                return jsonify({'error': str(e)})
        return jsonify({
            "message": "Upload realizado com sucesso",
            "vendas importados": len(sales_to_insert),
            "erros encontrados": error
        }), 200

@main_bp.route('/')
def index():
    return jsonify({"message":"Bem vindo ao Stiles"})
