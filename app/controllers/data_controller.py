from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import UserProfileModel, UserProfileMappingModel, UserModel
from flask import current_app


@jwt_required()
def create_profile():
    db = current_app.db
    profile_model = UserProfileModel(db)

    print(">>> ",request.headers)
    print(">>> ", request.data)
    try:
        data = request.get_json()
        user_id = data.get("user_id")
        profile_id = data.get("profile_id")
        profile_name = data.get("profile_name")
        profile_data = data.get("profile_data")
    except Exception as e:
        import traceback
        print(traceback.print_exc())

    if not all([user_id, profile_id, profile_name, profile_data]):
        return jsonify({"status": "error", "message": "All fields are required"}), 400

    result = profile_model.create_profile(user_id, profile_id, profile_name, profile_data)
    if result.inserted_id:
        return jsonify({"status": "success", "message": "Profile created successfully."}), 201

    return jsonify({"status": "error", "message": "Unable to create profile."}), 500

@jwt_required()
def get_records():
    db = current_app.db 
    record_model = UserProfileModel(db)

    user_id = get_jwt_identity()
    records = record_model.find_records_by_user(user_id)

    return jsonify({"records": records}), 200


@jwt_required()
def get_user_profile_mapping():
    db = current_app.db
    user_model = UserModel(db)
    user_profile_mapping_model = UserProfileMappingModel(db)

    # Retrieve user_id from query parameters
    user_id = request.args.get("user_id")
    if not user_id:
        return jsonify({"error": "user_id is required"}), 400

    # Query user details from the 'users' collection
    user = user_model.find_user_by_id(user_id)
    if not user:
        return jsonify({"error": f"User not found for user_id: {user_id}"}), 404

    # Query profiles from the 'user_profile_mapping' collection
    profiles = user_profile_mapping_model.get_profiles_by_user_id(user_id)
    profile_count = len(profiles)

    print("profiles: ",profiles)

    # Build the response
    response = {
        "user_id": user_id,
        "first_name": user.get("first_name"),
        "last_name": user.get("last_name"),
        "user_type": user.get("roles", ["user"])[0],  # Default role is 'user'
        "profile_count": profile_count,
        "profiles": profiles
    }

    return jsonify(response), 200


@jwt_required()
def get_profiles():
    db = current_app.db
    profile_model = UserProfileModel(db)

    user_id = request.args.get("user_id")

    print("here...")
    if not user_id:
        return jsonify({"status": "error", "message": "user_id is required"}), 400

    profiles = profile_model.get_profiles_by_user(user_id)
    for profile in profiles:
        print(profile)
    if not profiles:
        return jsonify({"status": "error", "message": "Unable to fetch profiles."}), 404

    return jsonify({"status": "success", "data": profiles}), 200


@jwt_required()
def edit_profile():
    db = current_app.db
    profile_model = UserProfileModel(db)

    data = request.get_json()
    profile_id = data.get("profile_id")
    user_id = data.get("user_id")
    profile_name = data.get("profile_name")
    profile_data = data.get("profile_data")

    if not all([user_id, profile_name, profile_data]):
        return jsonify({"status": "error", "message": "All fields are required"}), 400

    result = profile_model.update_profile(profile_id, user_id, profile_name, profile_data)
    if result.modified_count > 0:
        return jsonify({"status": "success", "message": "Profile updated successfully."}), 200

    return jsonify({"status": "error", "message": "Unable to update profile."}), 500

@jwt_required()
def delete_profile():
    print("HERE")
    db = current_app.db
    profile_model = UserProfileModel(db)

    data = request.get_json()
    user_id = data.get("user_id")
    profile_id = data.get("profile_id")

    if not user_id:
        return jsonify({"status": "error", "message": "user_id is required"}), 400

    result = profile_model.delete_profile(profile_id, user_id)
    if result.deleted_count > 0:
        return jsonify({"status": "success", "message": "Profile deleted successfully."}), 200

    return jsonify({"status": "error", "message": "Unable to delete profile."}), 500