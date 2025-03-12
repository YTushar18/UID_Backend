from flask import Flask
from pymongo import MongoClient
from flask_jwt_extended import JWTManager
from app.config import Config
from flask_cors import CORS

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # JWT Initialization
    jwt = JWTManager(app)

    # Enable CORS for all routes and origins
    CORS(app, resources={
    r"/*": {
        "origins": ["http://localhost:3001", "http://127.0.0.1:3001","http://192.168.1.97:3001", "*"],  # Allow Next.js dev server
        "allow_headers": ["Content-Type", "Authorization"],
        "methods": ["GET", "POST", "PUT", "DELETE"],
        "supports_credentials": True,
    }
})

    # MongoDB Connection
    client = MongoClient(app.config["MONGO_URI"])
    app.db = client.get_database("universal_identity_nexus")

    # Register Routes
    from app.routes import register_routes
    register_routes(app)

    return app