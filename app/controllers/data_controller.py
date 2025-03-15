from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import ProfileModel, UserModel
from app.models import UserApprovalRequestModel
from flask import current_app

@jwt_required()
def healthcheck():
    return jsonify({"status": "success", "message": "All systems are working fine"}), 201

# This API will return key metrics for the User Dashboard.
@jwt_required()
def get_user_dashboard_summary():
    db = current_app.db
    user_id = get_jwt_identity()

    # Collections
    profile_model = db.user_profile_data
    request_model = db.user_approval_requests

    # Fetch total profiles
    total_profiles = profile_model.count_documents({"user_id": user_id})

    # Fetch request counts
    pending_requests = request_model.count_documents({"user_id": user_id, "status": "Pending"})
    accepted_requests = request_model.count_documents({"user_id": user_id, "status": "Approved"})
    rejected_requests = request_model.count_documents({"user_id": user_id, "status": "Rejected"})

    # Fetch recent profiles (last 3 updated/created)
    recent_profiles = list(profile_model.find(
        {"user_id": user_id}, 
        {"_id": 1, "profile_name": 1, "updated_at": 1}
    ).sort("updated_at", -1).limit(3))

    # Convert ObjectId to string
    for profile in recent_profiles:
        profile["_id"] = str(profile["_id"])

    # Fetch recent requests (last 3)
    recent_requests = list(request_model.find(
        {"user_id": user_id},
        {"_id": 1, "vendor_name": 1, "profile_name": 1, "status": 1, "timestamp": 1}
    ).sort("timestamp", -1).limit(3))

    # Convert ObjectId to string
    for request in recent_requests:
        request["_id"] = str(request["_id"])

    return jsonify({
        "status": "success",
        "total_profiles": total_profiles,
        "pending_requests": pending_requests,
        "accepted_requests": accepted_requests,
        "rejected_requests": rejected_requests,
        "recent_profiles": recent_profiles,
        "recent_requests": recent_requests
    }), 200


@jwt_required()
def create_profile():
    db = current_app.db
    profile_model = ProfileModel(db)

    data = request.get_json()
    user_id = data.get("user_id")
    profile_name = data.get("profile_name")
    profile_data = data.get("profile_data")

    ALLOWED_PROFILES = ["General", "Job Hunt", "Gaming", "Shopping", "Education", "Social"]

    if not all([user_id, profile_name, profile_data]):
        return jsonify({"status": "error", "message": "user_id, profile_name, and profile_data are required"}), 400

    if profile_name not in ALLOWED_PROFILES:
        return jsonify({"status": "error", "message": f"Invalid profile name. Allowed profiles: {ALLOWED_PROFILES}"}), 400

    # Check if the user already has this profile
    existing_profile = profile_model.get_profile_by_name(user_id, profile_name)
    if existing_profile:
        return jsonify({"status": "error", "message": f"Profile '{profile_name}' already exists for this user"}), 400

    # Create new profile
    result = profile_model.create_profile(user_id, profile_name, profile_data)
    if result.inserted_id:
        return jsonify({"status": "success", "message": f"Profile created successfully"}), 201

    return jsonify({"status": "error", "message": "Unable to create profile"}), 500

@jwt_required()
def get_profiles():
    db = current_app.db
    user_model = UserModel(db)
    profile_model = ProfileModel(db)

    # Get user_id from query parameters
    user_id = request.args.get("user_id")
    if not user_id:
        return jsonify({"status": "error", "message": "user_id is required"}), 400

    # Fetch user details from 'users' collection
    user = user_model.find_user_by_id(user_id)
    if not user:
        return jsonify({"status": "error", "message": "User not found"}), 404

    # Fetch all profiles for the user
    profiles = profile_model.get_profiles_by_user(user_id)
    if not profiles:
        return jsonify({"status": "error", "message": "No profiles found"}), 404

    # Extract profile names and data
    profile_data = {profile["profile_name"]: profile["profile_data"] for profile in profiles}

    return jsonify({
        "user_id": user_id,
        "first_name": user.get("first_name"),
        "last_name": user.get("last_name"),
        "user_type": user.get("roles", ["user"])[0],
        "profile_count": len(profiles),
        "profiles": profile_data,
        "total_no_of_requests": 100  # Placeholder
    }), 200


@jwt_required()
def edit_profile():
    db = current_app.db
    profile_model = ProfileModel(db)

    data = request.get_json()
    user_id = data.get("user_id")
    profile_name = data.get("profile_name")
    profile_data = data.get("profile_data")

    if not all([user_id, profile_name, profile_data]):
        return jsonify({"status": "error", "message": "user_id, profile_name, and profile_data are required"}), 400

    # Check if profile exists
    existing_profile = profile_model.get_profile_by_name(user_id, profile_name)
    if not existing_profile:
        return jsonify({"status": "error", "message": f"Profile '{profile_name}' not found for this user"}), 404

    # Update profile
    result = profile_model.update_profile(user_id, profile_name, profile_data)
    if result.modified_count > 0:
        return jsonify({"status": "success", "message": f"Profile updated successfully"}), 200

    return jsonify({"status": "error", "message": "Unable to update profile"}), 500

@jwt_required()
def delete_profile():
    db = current_app.db
    profile_model = ProfileModel(db)

    data = request.get_json()
    user_id = data.get("user_id")
    profile_name = data.get("profile_name")  # Now taken from request body

    if not all([user_id, profile_name]):
        return jsonify({"status": "error", "message": "user_id and profile_name are required"}), 400

    # Check if profile exists
    existing_profile = profile_model.get_profile_by_name(user_id, profile_name)
    if not existing_profile:
        return jsonify({"status": "error", "message": f"Profile '{profile_name}' not found for this user"}), 404

    # Delete profile
    result = profile_model.delete_profile(user_id, profile_name)
    if result.deleted_count > 0:
        return jsonify({"status": "success", "message": f"Profile deleted successfully"}), 200

    return jsonify({"status": "error", "message": "Unable to delete profile"}), 500


# @jwt_required()
# def get_requests_for_user():
#     db = current_app.db
#     request_log_model = VendorRequestLogModel(db)

#     # Extract user_id from query parameters
#     user_id = request.args.get("user_id")
#     if not user_id:
#         return jsonify({"status": "error", "message": "user_id is required"}), 400

#     # Fetch all requests made for this user
#     logs = list(request_log_model.get_logs_by_user(user_id))
#     total_requests = len(logs)

#     return jsonify({
#         "status": "success",
#         "total_requests": total_requests,
#         "logs": logs
#     }), 200


# API for User Approval/Rejection
# This API allows users to approve or reject vendor requests.
@jwt_required()
def update_request_status():
    db = current_app.db
    request_model = UserApprovalRequestModel(db)

    user_id = get_jwt_identity()
    data = request.get_json()
    request_id = data.get("request_id")
    status = data.get("status")  # "Approved" or "Rejected"

    if status not in ["Approved", "Rejected"]:
        return jsonify({"status": "error", "message": "Invalid status"}), 400

    updated = request_model.update_request_status(request_id, user_id, status)

    if updated:
        return jsonify({"status": "success", "message": f"Request {status}"}), 200
    return jsonify({"status": "error", "message": "Request not found or unauthorized"}), 404



# API to Fetch All Requests for a User (User Dashboard)
# This API returns all requests for the logged-in user (both pending and approved/rejected).

@jwt_required()
def get_user_requests():
    db = current_app.db
    request_model = UserApprovalRequestModel(db)
    vendor_model = db.vendors  # Reference to vendors collection

    user_id = get_jwt_identity()
    requests = request_model.get_requests_for_user(user_id)

    # Convert ObjectId to string and fetch vendor details
    for req in requests:
        req["_id"] = str(req["_id"])  # Convert ObjectId to string
        
        # Fetch vendor details
        vendor = vendor_model.find_one({"vendor_id": req["vendor_id"]}, {"_id": 0, "client_type": 1, "website_url": 1})
        if vendor:
            req["vendor_type"] = vendor.get("client_type", "Unknown")
            req["vendor_website"] = vendor.get("website_url", "N/A")
        else:
            req["vendor_type"] = "Unknown"
            req["vendor_website"] = "N/A"

    return jsonify({"status": "success", "requests": requests}), 200