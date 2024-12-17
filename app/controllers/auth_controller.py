from flask import request, jsonify
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from app.models import UserModel, ClientModel
from flask import current_app

def register_user():
    db = current_app.db  # Access the app's MongoDB client dynamically
    user_model = UserModel(db)
    client_model = ClientModel(db)

    data = request.get_json()

    if data['type'] == "user":
        email = data.get("email")
        password = data.get("password")
        first_name = data.get("first_name")
        last_name = data.get("last_name")

        if user_model.find_user_by_email(email):
            return jsonify({"message": "User already exists"}), 400

        user_model.create_user(email, password, first_name, last_name)
        return jsonify({"message": "User registered successfully"}), 201
    
    if data['type'] == "client":
        email = data.get("email")
        password = data.get("password")
        org_name = data.get("org_name")
        admin_name = data.get("admin_name")
        client_type = data.get("client_type")

        if client_model.find_client_by_email(email):
            return jsonify({"message": "Client already exists"}), 400

        client_model.create_client(email, password, org_name, admin_name, client_type)
        return jsonify({"message": "Client registered successfully"}), 201


def login_user():
    db = current_app.db  # Get database instance
    user_model = UserModel(db)

    # Parse input data
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    # Validate credentials
    user = user_model.validate_password(email, password)
    if not user:
        return jsonify({"message": "Invalid credentials"}), 401

    # Extract user_id from user document
    user_id = user["user_id"]

    # Generate JWT tokens
    access_token = create_access_token(identity=user_id)
    refresh_token = create_refresh_token(identity=user_id)

    # Return user_id with tokens
    return jsonify({
        "user_id": user_id,
        "access_token": access_token,
        "refresh_token": refresh_token
    }), 200


@jwt_required(refresh=True)
def refresh_token():
    current_user = get_jwt_identity()
    new_access_token = create_access_token(identity=current_user)
    return jsonify({"access_token": new_access_token}), 200