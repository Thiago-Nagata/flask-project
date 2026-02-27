from flask import Blueprint, jsonify, redirect, render_template, request
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

# Dashboard
@main_bp.route('/dashboard', methods=['GET'])
@token_required
def dashboard(token):
    total_products = db.products.count_documents({})

    return render_template("dashboard.html", total_products=total_products)

# Rota de produtos
@main_bp.route('/products', methods=['GET'])
@token_required
def get_products(current_user):
    products = list(db.products.find())
    return render_template("products.html", products=products)

@main_bp.route('/products/add', methods=['GET'])
@token_required
def create_product_interface(current_user):
    return render_template("add_product.html")

# Criar produto
@main_bp.route('/products/add', methods=['POST'])
@token_required
def create_product(current_user):

    new_product_data = {
        "name": request.form.get("name"),
        "price": request.form.get("price"),
        "description": request.form.get("description"),
        "stock": request.form.get("stock")
    }
    
    db.products.insert_one(new_product_data)
    return redirect("/products") 

@main_bp.route('/products/<string:product_id>', methods=['GET'])
@token_required
def get_product_by_id(token, product_id):
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

@main_bp.route('/products/edit/<string:product_id>', methods=['GET'])
@token_required
def edit_product(current_user, product_id):
    try:
        produto = db.products.find_one({"_id": ObjectId(product_id)})
    except:
        return redirect("/products")

    if not produto:
        return redirect("/products")

    produto["_id"] = str(produto["_id"])
    return render_template("edit_product.html", produto=produto)

@main_bp.route('/products/edit/<string:product_id>', methods=['POST'])
@token_required
def update_product(current_user, product_id):
    method = request.form.get("_method")

    if method == "PUT":
        update_data ={
            "name": request.form.get("name"),
            "price": float(request.form.get("price")),
            "stock": int(request.form.get("stock"))
        }

        db.products.update_one(
            {"_id": ObjectId(product_id)},
            {"$set": update_data}
        )
        return redirect("/products")
    
    if method == "DELETE":
        db.products.delete_one({"_id": ObjectId(product_id)})
        return redirect("/products")
        
    return "Método Invalido", 400

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
