from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import UserProfileModel, UserProfileMappingModel, UserModel
from flask import current_app


@jwt_required()
def create_record():
    db = current_app.db 
    user_profile_data = UserProfileModel(db)
    user_profile_mapping_model = UserProfileMappingModel(db)
    users_data = UserModel(db)

    email = get_jwt_identity()
    user_id = users_data.get_user_id_by_email(email)

    data = request.get_json()

    result_mapping = user_profile_mapping_model.create_user_profile_mapping(user_id,data)

    if result_mapping:
        result = user_profile_data.create_profile_data(user_id, data)
        return jsonify({"record_id": str(result.inserted_id)}), 201
    
    return jsonify({"Message": "Record not added"}), 201

@jwt_required()
def get_records():
    db = current_app.db 
    record_model = UserProfileModel(db)

    user_id = get_jwt_identity()
    records = record_model.find_records_by_user(user_id)

    return jsonify({"records": records}), 200