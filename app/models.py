from bson import ObjectId
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

class UserModel:
    def __init__(self, db):
        self.collection = db.users

    def create_user(self, email, password, first_name, last_name):
        hashed_password = generate_password_hash(password)
        user = {"email": email, "password": hashed_password, "roles": ["user"], "first_name":first_name, "last_name": last_name}
        return self.collection.insert_one(user)

    def find_user_by_email(self, email):
        return self.collection.find_one({"email": email})

    def validate_password(self, email, password):
        user = self.find_user_by_email(email)
        if user and check_password_hash(user["password"], password):
            return user
        return None
    

class RecordModel:
    def __init__(self, db):
        self.collection = db.records

    def create_record(self, user_id, data):
        record = {
            "user_id": user_id,
            "data": data,
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
        }
        return self.collection.insert_one(record)

    def find_records_by_user(self, user_id):
        return list(self.collection.find({"user_id": user_id}))

    def update_record(self, record_id, data):
        return self.collection.update_one(
            {"_id": ObjectId(record_id)},
            {"$set": {"data": data, "updated_at": datetime.now()}},
        )

    def delete_record(self, record_id):
        return self.collection.delete_one({"_id": ObjectId(record_id)})
    

