from flask import request, jsonify
from app.models import VendorModel
from flask import current_app

def authenticate_vendor():
    db = current_app.db
    vendor_model = VendorModel(db)

    api_key = request.headers.get("Authorization")
    if not api_key or not api_key.startswith("Bearer "):
        return jsonify({"status": "error", "message": "API Key is required"}), 401

    api_key = api_key.split(" ")[1]  # Extract the token

    vendor = vendor_model.validate_vendor_api_key(api_key)
    if not vendor:
        return jsonify({"status": "error", "message": "Invalid API Key"}), 403

    return vendor["vendor_id"]