from flask import Flask
from pymongo import MongoClient
from flask_jwt_extended import JWTManager
from app.config import Config

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # JWT Initialization
    jwt = JWTManager(app)

    # MongoDB Connection
    client = MongoClient(app.config["MONGO_URI"])
    app.db = client.get_database("universal_identity_nexus")

    # Register Routes
    from app.routes import register_routes
    register_routes(app)

    return app