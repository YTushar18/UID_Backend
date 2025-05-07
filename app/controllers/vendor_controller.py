from flask import request, jsonify
import json
from app.utils import send_email
from flask import Response
from collections import defaultdict
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask import current_app
from app.middleware import authenticate_vendor
from app.models import ProfileModel, UserApprovalRequestModel, CustomRequestModel

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
    comments = data.get("comments")

    if not all([unique_user_id, profile_name]):
        return jsonify({"status": "error", "message": "Missing required fields"}), 400

    # Log request as pending
    request_model.create_request(vendor["vendor_id"], vendor["vendor_name"], vendor["website_url"], unique_user_id, profile_name, comments)

    return jsonify({"status": "success", "message": "Request logged and pending approval"}), 201

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
    user_model = db.users  # Reference to users collection

    # Fetch all requests for the vendor
    requests = list(request_model.find(
        {"vendor_id": vendor_id},
        {"_id": 1, "user_id": 1, "profile_name": 1, "status": 1, "timestamp": 1}
    ).sort("timestamp", -1))

    # Convert ObjectId to string and replace user_id with username
    for req in requests:
        req["_id"] = str(req["_id"])

        # Fetch username from users collection
        user = user_model.find_one({"user_id": req["user_id"]}, {"_id": 0, "username": 1})
        req["username"] = user["username"] if user else "Unknown"

        # Remove user_id from response
        del req["user_id"]

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
    username = data.get("unique_user_id")  # unique_user_id is actually the username
    profile_name = data.get("profile_name")
    comments = data.get("comments")

    if not all([username, profile_name]):
        return jsonify({"status": "error", "message": "Missing required fields"}), 400
    
    vendor_id = get_jwt_identity()

    # Validate Vendor
    vendor = db.vendors.find_one({"vendor_id": vendor_id})
    if not vendor:
        return jsonify({"status": "error", "message": "Invalid Vendor"}), 403

    # Validate User by checking username in the users collection
    user = db.users.find_one({"username": username}, {"_id": 0, "user_id": 1})
    if not user:
        return jsonify({"status": "error", "message": "User not found"}), 404

    # Extract the actual user_id from the query result
    user_id = user["user_id"]

    # Log request as pending
    request_model.create_request(vendor["vendor_id"], vendor["vendor_name"], vendor["website_url"], user_id, profile_name, comments)

    # After request_model.create_request(...)
    # user = db.users.find_one({"username": username}, {"_id": 0, "email": 1, "first_name": 1})
    # if user:
    #     user_email = user.get("email")
    #     user_name = user.get("first_name", "User")

    #     subject = f"New Data Access Request from {vendor['vendor_name']}"
    #     content = f"""
    #                 Hi {user_name},

    #                 You have a new request from {vendor['vendor_name']} ({vendor['website_url']}) to access your profile: {profile_name}.

    #                 Please log in to your dashboard to approve or reject this request.

    #                 Thank you,
    #                 Universal Identity Nexus
    #                 """
    #     print("Sending email to:", user_email)
    #     print("Subject:", subject)
    #     print("Content:", content)
    #     response = send_email(user_email, subject, content)
    #     if response.status_code != 200:
    #         print("Mailgun Error:", response.text)

    return jsonify({"status": "success", "message": "Request logged and pending approval"}), 201




@jwt_required()
def create_data_request_from_dashboard_custom():
    db = current_app.db
    custom_request_model = CustomRequestModel(db)

    # Parse request data
    data = request.get_json()
    username = data.get("username")  # unique_user_id is actually the username
    custom_fields = data.get("custom_fields")  # This should be a list of field keys
    comments = data.get("comments")

    if not username or not custom_fields or not isinstance(custom_fields, dict):
        return jsonify({"status": "error", "message": "Username and custom_fields list are required"}), 400

    vendor_id = get_jwt_identity()

    # Validate Vendor
    vendor = db.vendors.find_one({"vendor_id": vendor_id})
    if not vendor:
        return jsonify({"status": "error", "message": "Invalid Vendor"}), 403

    # Validate User by checking username in the users collection
    user = db.users.find_one({"username": username}, {"_id": 0, "user_id": 1})
    if not user:
        return jsonify({"status": "error", "message": "User not found"}), 404

    # Extract the actual user_id from the query result
    user_id = user["user_id"]

    # Transform list of keys into a dictionary
    structured_fields = {key: "" for key in custom_fields}

    # Log request as pending in the custom requests table
    custom_request_model.create_custom_request(
        vendor["vendor_id"],
        vendor["vendor_name"],
        vendor["website_url"],
        user_id,
        structured_fields,
        comments
    )

    # After request_model.create_request(...)
    # user = db.users.find_one({"username": username}, {"_id": 0, "email": 1, "first_name": 1})
    # if user:
    #     user_email = user.get("email")
    #     user_name = user.get("first_name", "User")

    #     subject = f"New Data Access Request from {vendor['vendor_name']}"
    #     content = f"""
    #                 Hi {user_name},

    #                 You have a new request from {vendor['vendor_name']} ({vendor['website_url']}) to access your profile: {profile_name}.

    #                 Please log in to your dashboard to approve or reject this request.

    #                 Thank you,
    #                 Universal Identity Nexus
    #                 """
        
    #     print("Sending email to:", user_email)
    #     print("Subject:", subject)
    #     print("Content:", content)

    #     response = send_email(user_email, subject, content)
    #     if response.status_code != 200:
    #         print("Mailgun Error:", response.text)

    return jsonify({"status": "success", "message": "Custom request logged and pending approval"}), 201



@jwt_required()
def get_vendor_custom_requests():
    db = current_app.db
    vendor_id = get_jwt_identity()

    # Collections
    custom_request_model = db.custom_requests
    user_model = db.users  # Reference to users collection

    # Fetch all custom requests for the vendor
    requests = list(custom_request_model.find(
        {"vendor_id": vendor_id},
        {"_id": 1, "user_id": 1, "custom_fields": 1, "comments": 1, "status": 1, "timestamp": 1}
    ).sort("timestamp", -1))

    # Convert ObjectId to string and replace user_id with username
    for req in requests:
        req["_id"] = str(req["_id"])

        # Fetch username from users collection
        user = user_model.find_one({"user_id": req["user_id"]}, {"_id": 0, "username": 1})
        req["username"] = user["username"] if user else "Unknown"

        # Remove user_id from response
        del req["user_id"]

    return jsonify({
        "status": "success",
        "total_custom_requests": len(requests),
        "requests": requests
    }), 200



@jwt_required()
def get_vendor_details():
    db = current_app.db
    vendor_id = get_jwt_identity()

    # Fetch vendor details from the vendors collection
    vendor = db.vendors.find_one({"vendor_id": vendor_id}, {"_id": 0, "password": 0})

    if not vendor:
        return jsonify({"status": "error", "message": "Vendor not found"}), 404

    return jsonify({
        "status": "success",
        "vendor": vendor
    }), 200


@jwt_required()
def update_vendor_details():
    db = current_app.db
    vendor_id = get_jwt_identity()

    # Parse update fields
    data = request.get_json()
    allowed_fields = [
        "vendor_name", "website_url", "admin_name", 
        "admin_contact_phone", "client_type", "admin_contact"
    ]
    update_data = {key: value for key, value in data.items() if key in allowed_fields}

    if not update_data:
        return jsonify({"status": "error", "message": "No valid fields provided for update"}), 400

    # Update the vendor record
    result = db.vendors.update_one(
        {"vendor_id": vendor_id},
        {"$set": update_data}
    )

    if result.modified_count == 0:
        return jsonify({"status": "warning", "message": "No changes made or vendor not found"}), 200

    return jsonify({"status": "success", "message": "Vendor details updated successfully"}), 200

@jwt_required()
def get_vendor_dashboard_analytics():
    db = current_app.db
    vendor_id = get_jwt_identity()

    vendor = db.vendors.find_one({"vendor_id": vendor_id}, {"risk_score": 1})
    risk_score = vendor.get("risk_score", 0) if vendor else 0

    request_model = db.user_approval_requests
    vendor_requests = list(request_model.find({"vendor_id": vendor_id}))

    total_requests = len(vendor_requests)
    status_counts = defaultdict(int)
    profile_counts = defaultdict(int)
    requests_by_date = defaultdict(int)
    status_over_time = defaultdict(lambda: defaultdict(int))

    for r in vendor_requests:
        status_counts[r["status"]] += 1
        profile_counts[r["profile_name"]] += 1

        date_key = r["timestamp"].strftime("%Y-%m-%d")
        requests_by_date[date_key] += 1
        status_over_time[date_key][r["status"]] += 1

    approval_rate = (status_counts["Approved"] / total_requests * 100) if total_requests > 0 else 0
    recent_requests = sorted(vendor_requests, key=lambda x: x["timestamp"], reverse=True)[:3]

    return jsonify({
        "status": "success",
        "data": {
            "active_requests": status_counts["Pending"],
            "verified_users": status_counts["Approved"],
            "rejected_requests": status_counts["Rejected"],
            "risk_score": risk_score,
            "approval_rate": round(approval_rate, 2),
            "recent_requests": [
                {
                    "username": r.get("username", "Unknown"),
                    "profile_name": r.get("profile_name"),
                    "status": r.get("status"),
                    "timestamp": r.get("timestamp").isoformat()
                }
                for r in recent_requests
            ],
            "chart_data": {
                "requests_by_date": dict(requests_by_date),
                "status_over_time": {k: dict(v) for k, v in status_over_time.items()},
                "profile_request_distribution": dict(profile_counts)
            }
        }
    }), 200