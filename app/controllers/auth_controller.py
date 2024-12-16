from flask import request, jsonify
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from app.models import UserModel
from flask import current_app

def register_user():
    db = current_app.db  # Access the app's MongoDB client dynamically
    user_model = UserModel(db)

    data = request.get_json()
    email = data.get("email")
    password = data.get("password")
    first_name = data.get("first_name")
    last_name = data.get("last_name")

    if user_model.find_user_by_email(email):
        return jsonify({"message": "User already exists"}), 400

    user_model.create_user(email, password, first_name, last_name)
    return jsonify({"message": "User registered successfully"}), 201

def login_user():
    db = current_app.db  # Access the app's MongoDB client dynamically
    user_model = UserModel(db)

    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    user = user_model.validate_password(email, password)
    if not user:
        return jsonify({"message": "Invalid credentials"}), 401

    access_token = create_access_token(identity=email)
    refresh_token = create_refresh_token(identity=email)
    return jsonify({"access_token": access_token, "refresh_token": refresh_token}), 200

@jwt_required(refresh=True)
def refresh_token():
    current_user = get_jwt_identity()
    new_access_token = create_access_token(identity=current_user)
    return jsonify({"access_token": new_access_token}), 200