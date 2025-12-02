from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
"""

# app/__init__.py
"""
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from .config import Config

db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)

    from .routes.inventory_routes import inventory_bp
    app.register_blueprint(inventory_bp, url_prefix="/api/inventory")

    return app
"""

# app/config.py
"""
import os
from dotenv import load_dotenv
load_dotenv()

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "postgresql://user:pass@localhost:5432/inventory")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
"""

# app/models.py
"""
from . import db
from datetime import datetime

class Product(db.Model):
    __tablename__ = "products"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    sku = db.Column(db.String(100), unique=True, nullable=False)
    stock = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
"""

# app/routes/inventory_routes.py
"""
from flask import Blueprint, request, jsonify
from app.models import Product
from app import db
from app.services.inventory_service import InventoryService

inventory_bp = Blueprint("inventory", __name__)

@inventory_bp.get("/")
def get_all():
    return InventoryService.get_all()

@inventory_bp.post("/")
def create():
    data = request.json
    return InventoryService.create(data)

@inventory_bp.put("/<int:id>")
def update(id):
    data = request.json
    return InventoryService.update(id, data)

@inventory_bp.delete("/<int:id>")
def delete(id):
    return InventoryService.delete(id)
"""

# app/services/inventory_service.py
"""
from flask import jsonify
from app.models import Product
from app import db

class InventoryService:

    @staticmethod
    def get_all():
        items = Product.query.all()
        return jsonify([{
            "id": i.id,
            "name": i.name,
            "sku": i.sku,
            "stock": i.stock,
            "created_at": i.created_at,
            "updated_at": i.updated_at
        } for i in items])

    @staticmethod
    def create(data):
        item = Product(**data)
        db.session.add(item)
        db.session.commit()
        return jsonify({"message": "created", "id": item.id})

    @staticmethod
    def update(id, data):
        item = Product.query.get_or_404(id)
        for k, v in data.items():
            setattr(item, k, v)
        db.session.commit()
        return jsonify({"message": "updated"})

    @staticmethod
    def delete(id):
        item = Product.query.get_or_404(id)
        db.session.delete(item)
        db.session.commit()
        return jsonify({"message": "deleted"})
"""

# docker-compose.yml
"""
version: "3.9"
services:
  db:
    image: postgres:15
    container_name: inventory_db
    environment:
      POSTGRES_USER: user
      POSTGRES_PASSWORD: pass
      POSTGRES_DB: inventory
    ports:
      - "5432:5432"
    volumes:
      - pgdata:/var/lib/postgresql/data
volumes:
  pgdata:
"""

# requirements.txt
"""
Flask
Flask_SQLAlchemy
Flask_Migrate
python-dotenv
psycopg2-binary
"""

# .env.example
"""
DATABASE_URL=postgresql://user:pass@localhost:5432/inventory
"""

# === Additional Enhancements (Options A–E) ===

# A) tests/test_inventory.py (pytest sample)
"""
import json

def test_get_all(client):
    res = client.get('/api/inventory/')
    assert res.status_code == 200


def test_create_product(client):
    payload = {"name": "Test", "sku": "SKU-1", "stock": 10}
    res = client.post('/api/inventory/', json=payload)
    assert res.status_code == 200
"""

# tests/conftest.py (Flask test client)
"""
import pytest
from app import create_app, db

@pytest.fixture
def app():
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'

    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()
"""

# B) Swagger / OpenAPI (flask-swagger-ui)
# app/swagger.py
"""
def get_swagger_spec():
    return {
        "openapi": "3.0.0",
        "info": {"title": "Inventory API", "version": "1.0"},
        "paths": {
            "/api/inventory/": {
                "get": {"summary": "Get all products"},
                "post": {"summary": "Create product"}
            }
        }
    }
"""

# app/routes/swagger_routes.py
"""
from flask import Blueprint, jsonify
from app.swagger import get_swagger_spec

swagger_bp = Blueprint("swagger", __name__)

@swagger_bp.get("/swagger.json")
def swagger_spec():
    return jsonify(get_swagger_spec())
"""

# Add in create_app()
# app.register_blueprint(swagger_bp)

# C) JWT Auth (simple)
# app/routes/auth_routes.py
"""
from flask import Blueprint, request, jsonify
import jwt, datetime

auth_bp = Blueprint('auth', __name__)
SECRET = "SECRET_KEY_CHANGE_ME"

@auth_bp.post('/login')
def login():
    data = request.json
    if data.get('username') == 'admin' and data.get('password') == '123':
        token = jwt.encode({
            'user': 'admin',
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=12)
        }, SECRET, algorithm='HS256')
        return jsonify({"token": token})
    return jsonify({"error": "invalid credentials"}), 401
"""

# Decorator for protected routes
"""
from functools import wraps
from flask import request

def require_auth(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return {"error": "Missing token"}, 401
        try:
            jwt.decode(token, SECRET, algorithms=['HS256'])
        except:
            return {"error": "Invalid token"}, 401
        return f(*args, **kwargs)
    return wrapper
"""

# Use in routes:
# @inventory_bp.get('/')
# @require_auth

# D) GitHub Actions CI
# .github/workflows/tests.yml
"""
name: Run Tests

on: [push]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'

    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install pytest

    - name: Run tests
      run: pytest -v
"""

# E) Minimal Frontend (Tabulator)
# public/index.html
"""
<!DOCTYPE html>
<html>
<head>
  <script src="https://unpkg.com/tabulator-tables@5.4.4/dist/js/tabulator.min.js"></script>
  <link href="https://unpkg.com/tabulator-tables@5.4.4/dist/css/tabulator.min.css" rel="stylesheet">
</head>
<body>
<div id="inventory-table"></div>

<script>
  const table = new Tabulator("#inventory-table", {
    ajaxURL: "/api/inventory/",
    layout: "fitColumns",
    columns: [
      {title:"ID", field:"id"},
      {title:"Name", field:"name"},
      {title:"SKU", field:"sku"},
      {title:"Stock", field:"stock"}
    ]
  });
</script>
</body>
</html>
"""
