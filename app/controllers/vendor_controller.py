from flask import request, jsonify
import json
from flask import Response
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask import current_app
from app.middleware import authenticate_vendor
from app.models import VendorModel, ProfileModel, UserModel, VendorRequestLogModel, UserApprovalRequestModel

# def fetch_user_profile():
#     db = current_app.db
#     vendor_model = VendorModel(db)
#     profile_model = ProfileModel(db)
#     user_model = UserModel(db)
#     request_log_model = VendorRequestLogModel(db)  # Instantiate logging model

#     # Get API key from headers
#     api_key = request.headers.get("Authorization")
#     if not api_key or not api_key.startswith("Bearer "):
#         return jsonify({"status": "error", "message": "Missing or invalid API Key"}), 401

#     # Extract actual key from "Bearer <API_KEY>"
#     api_key = api_key.split(" ")[1]

#     # Validate API Key
#     vendor = vendor_model.validate_vendor_api_key(api_key)
#     if not vendor:
#         return jsonify({"status": "error", "message": "Invalid API Key"}), 403

#     vendor_id = vendor["vendor_id"]

#     # Extract request data
#     data = request.get_json()
#     unique_user_id = data.get("unique_user_id")
#     profile_name = data.get("profile_name")

#     if not all([unique_user_id, profile_name]):
#         return jsonify({"status": "error", "message": "unique_user_id and profile_name are required"}), 400

#     # Check if user exists
#     user = user_model.find_user_by_id(unique_user_id)
#     if not user:
#         return jsonify({"status": "error", "message": "User not found"}), 404

#     # Fetch the user's profile
#     profile = profile_model.get_profile_by_name(unique_user_id, profile_name)
#     if not profile:
#         return jsonify({"status": "error", "message": "Profile not found"}), 404

#     # Log the vendor request
#     request_log_model.log_vendor_request(vendor_id, unique_user_id, profile_name)

#     # Return profile data (excluding sensitive information)
#     filtered_data = {key: value for key, value in profile["profile_data"].items() if key != "ssn"}

#     return jsonify({
#         "status": "success",
#         "user_id": unique_user_id,
#         "profile_name": profile_name,
#         "profile_data": filtered_data
#     }), 200


# Vendor Fetch User Data API
# This API will log a request instead of returning data immediately. The request will be marked as pending until the user approves it.
def vendor_fetch_user_data():
    db = current_app.db
    request_model = UserApprovalRequestModel(db)

    # Extract API Key from Authorization Header
    api_key = request.headers.get("Authorization")
    if not api_key or not api_key.startswith("Bearer "):
        return jsonify({"status": "error", "message": "Missing or invalid API key"}), 401

    api_key = api_key.split("Bearer ")[1]

    # Validate API Key
    vendor = db.vendors.find_one({"vendor_api_key": api_key})
    if not vendor:
        return jsonify({"status": "error", "message": "Invalid API key"}), 403

    # Parse request data
    data = request.get_json()
    unique_user_id = data.get("unique_user_id")
    profile_name = data.get("profile_name")

    if not all([unique_user_id, profile_name]):
        return jsonify({"status": "error", "message": "Missing required fields"}), 400

    # Log request as pending
    request_model.create_request(vendor["vendor_id"], vendor["vendor_name"], vendor["website_url"], unique_user_id, profile_name)

    return jsonify({"status": "success", "message": "Request logged and pending approval"}), 201


@jwt_required()
def get_vendor_requests():
    db = current_app.db
    request_log_model = VendorRequestLogModel(db)

    # Extract vendor ID from JWT token
    vendor_id = get_jwt_identity()

    # Fetch request logs for the vendor
    logs = list(request_log_model.get_logs_by_vendor(vendor_id))
    
    return jsonify({"status": "success", "logs": logs}), 200


# API to Fetch All Requests Made by a Vendor (Vendor Dashboard)
# This API returns all vendor requests, so vendors can track pending, approved, and rejected requests.
@jwt_required()
def get_vendor_requests():
    db = current_app.db
    request_model = UserApprovalRequestModel(db)

    vendor_id = get_jwt_identity()
    requests = request_model.get_requests_for_vendor(vendor_id)

    return jsonify({"status": "success", "requests": requests}), 200


# API for Vendors to Download Approved Data
# Vendors can only download user data if the request is approved.

@jwt_required()
def download_approved_data():
    db = current_app.db
    request_model = UserApprovalRequestModel(db)
    profile_model = ProfileModel(db)

    vendor_id = get_jwt_identity()
    data = request.get_json()
    request_ids = data.get("request_ids")

    if not request_ids or not isinstance(request_ids, list):
        return jsonify({"status": "error", "message": "Request IDs must be a list"}), 400

    user_profiles = []

    if "ALL" in request_ids:
        # Fetch all approved requests for the vendor (FIX: Use request_model.collection)
        approved_requests = list(request_model.collection.find({"vendor_id": vendor_id, "status": "Approved"}))

        if not approved_requests:
            return jsonify({"status": "error", "message": "No approved requests found"}), 404

        # Fetch profile data for all approved requests
        for req in approved_requests:
            user_id = req["user_id"]
            profile_name = req["profile_name"]
            profile_data = profile_model.get_profile_by_name(user_id, profile_name)

            if profile_data:
                user_profiles.append({
                    "user_id": user_id,
                    "profile_name": profile_name,
                    "profile_data": profile_data["profile_data"]
                })

    else:
        # Fetch only selected approved requests
        for request_id in request_ids:
            request_data = request_model.get_request_by_id(request_id)
            if not request_data or request_data["status"] != "Approved":
                continue  # Skip if request is not approved

            # Ensure the vendor requesting matches the approved request
            if request_data["vendor_id"] != vendor_id:
                continue  # Skip unauthorized requests

            # Fetch user profile data
            user_id = request_data["user_id"]
            profile_name = request_data["profile_name"]
            profile_data = profile_model.get_profile_by_name(user_id, profile_name)

            if profile_data:
                user_profiles.append({
                    "user_id": user_id,
                    "profile_name": profile_name,
                    "profile_data": profile_data["profile_data"]
                })

    if not user_profiles:
        return jsonify({"status": "error", "message": "No profile data found for approved requests"}), 404

    # Convert to JSON and return as a downloadable file
    json_data = json.dumps(user_profiles, indent=4)
    return Response(json_data, mimetype="application/json", headers={"Content-Disposition": "attachment;filename=approved_profiles.json"})



@jwt_required()
def get_vendor_dashboard_summary():
    db = current_app.db
    vendor_id = get_jwt_identity()

    # Collections
    request_model = db.user_approval_requests

    # Fetch active (pending) requests
    active_requests = request_model.count_documents({"vendor_id": vendor_id, "status": "Pending"})

    # Fetch verified (approved) users
    verified_users = request_model.count_documents({"vendor_id": vendor_id, "status": "Approved"})

    # Fetch rejected requests
    rejected_requests = request_model.count_documents({"vendor_id": vendor_id, "status": "Rejected"})

    # Fetch recent requests (last 3 requests)
    recent_requests = list(request_model.find(
        {"vendor_id": vendor_id},
        {"_id": 1, "user_id": 1, "profile_name": 1, "status": 1, "timestamp": 1}
    ).sort("timestamp", -1).limit(3))

    # Convert ObjectId to string
    for request in recent_requests:
        request["_id"] = str(request["_id"])

    return jsonify({
        "status": "success",
        "active_requests": active_requests,
        "verified_users": verified_users,
        "rejected_requests": rejected_requests,
        "recent_requests": recent_requests
    }), 200


@jwt_required()
def get_vendor_requests_table():
    db = current_app.db
    vendor_id = get_jwt_identity()

    # Collections
    request_model = db.user_approval_requests

    # Fetch all requests for the vendor
    requests = list(request_model.find(
        {"vendor_id": vendor_id},
        {"_id": 1, "user_id": 1, "profile_name": 1, "status": 1, "timestamp": 1}
    ).sort("timestamp", -1))

    # Convert ObjectId to string
    for req in requests:
        req["_id"] = str(req["_id"])

    return jsonify({
        "status": "success",
        "total_requests": len(requests),
        "requests": requests
    }), 200


@jwt_required()
def create_data_request_from_dashboard():

    db = current_app.db
    request_model = UserApprovalRequestModel(db)

    # Parse request data
    data = request.get_json()
    unique_user_id = data.get("unique_user_id")
    profile_name = data.get("profile_name")

    if not all([unique_user_id, profile_name]):
        return jsonify({"status": "error", "message": "Missing required fields"}), 400
    
    vendor_id = get_jwt_identity()

    print(vendor_id)

    # Validate API Key
    vendor = db.vendors.find_one({"vendor_id": vendor_id})
    if not vendor:
        return jsonify({"status": "error", "message": "Invalid API key"}), 403

    # Log request as pending
    request_model.create_request(vendor["vendor_id"], vendor["vendor_name"], vendor["website_url"], unique_user_id, profile_name)

    return jsonify({"status": "success", "message": "Request logged and pending approval"}), 201