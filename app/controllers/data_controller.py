from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import RecordModel
from flask import current_app
from app.models import RecordModel

@jwt_required()
def create_record():
    db = current_app.db 
    record_model = RecordModel(db)

    user_id = get_jwt_identity()
    data = request.get_json()

    result = record_model.create_record(user_id, data)
    return jsonify({"record_id": str(result.inserted_id)}), 201

@jwt_required()
def get_records():
    db = current_app.db 
    record_model = RecordModel(db)

    user_id = get_jwt_identity()
    records = record_model.find_records_by_user(user_id)

    return jsonify({"records": records}), 200