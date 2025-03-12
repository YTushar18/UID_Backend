from flask import request, jsonify
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from app.models import UserModel, VendorModel
from flask import current_app



@jwt_required(refresh=True)
def refresh_token():
    current_user = get_jwt_identity()
    new_access_token = create_access_token(identity=current_user)
    return jsonify({"access_token": new_access_token}), 200



def register_user():
    db = current_app.db  # Access the app's MongoDB client dynamically
    user_model = UserModel(db)

    data = request.get_json()

    email = data.get("email")
    password = data.get("password")
    username = data.get("username")
    first_name = data.get("first_name")
    last_name = data.get("last_name")

    if user_model.find_user_by_email(email):
        return jsonify({"message": "User already exists"}), 400
    
    if user_model.find_user_by_username(username):
        return jsonify({"message": "Username already taken"}), 400

    user_model.create_user(email, username, password, first_name, last_name)
    return jsonify({"message": "User registered successfully"}), 201


def login_user():
    db = current_app.db
    user_model = UserModel(db)

    # Parse input data
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")
    # login_type = data.get("login_type")

    
    # Authenticate using users table
    user = user_model.validate_password(email, password)
    if not user:
        return jsonify({"message": "Invalid credentials"}), 401
    
    user_id = user["user_id"]
    response_data = {
        "user_id": user_id
    }

    # Generate JWT tokens
    access_token = create_access_token(identity=user_id)
    refresh_token = create_refresh_token(identity=user_id)

    # Return user_id with tokens, adding `org_name` only for clients
    response_data.update({
        "access_token": access_token,
        "refresh_token": refresh_token
    })

    return jsonify(response_data), 200

def register_vendor():
    db = current_app.db
    vendor_model = VendorModel(db)

    data = request.get_json()
    vendor_name = data.get("vendor_name")  # Organization Name
    website_url = data.get("website_url")
    admin_name = data.get("admin_name")
    admin_contact_phone = data.get("admin_contact_phone")  # Contact Number
    client_type = data.get("client_type")  # Type of Organization
    admin_contact = data.get("admin_contact")  # Admin Email
    password = data.get("password")  # Password

    if not all([vendor_name, website_url, admin_name, admin_contact_phone, client_type, admin_contact, password]):
        return jsonify({"status": "error", "message": "All fields are required"}), 400

    # Check if vendor already exists (by email)
    if vendor_model.find_vendor_by_email(admin_contact):
        return jsonify({"status": "error", "message": "Vendor with this email already exists"}), 400

    # Create vendor and generate API key
    vendor_data = vendor_model.create_vendor(vendor_name, website_url, admin_name, admin_contact_phone, client_type, admin_contact, password)

    return jsonify({
        "status": "success",
        "vendor_id": vendor_data["vendor_id"],
        "vendor_api_key": vendor_data["vendor_api_key"],
        "message": "Vendor registered successfully"
    }), 201

def vendor_login():
    db = current_app.db
    vendor_model = VendorModel(db)

    # Parse input data
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    # Validate credentials
    vendor = vendor_model.validate_vendor_credentials(email, password)
    if not vendor:
        return jsonify({"message": "Invalid credentials"}), 401

    vendor_id = vendor["vendor_id"]

    # Generate JWT tokens
    access_token = create_access_token(identity=vendor_id)
    refresh_token = create_refresh_token(identity=vendor_id)

    # Return vendor_id with tokens
    return jsonify({
        "vendor_id": vendor_id,
        "access_token": access_token,
        "refresh_token": refresh_token
    }), 200