from bson import ObjectId
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import uuid

class UserModel:
    def __init__(self, db):
        self.collection = db.users

    def create_user(self, email, password, first_name, last_name):
        hashed_password = generate_password_hash(password)
        user_id = str(uuid.uuid4()) 
        user = {
                    "user_id": user_id, 
                    "email": email,
                    "password": hashed_password,
                    "roles": ["user"],
                    "first_name": first_name,
                    "last_name": last_name,
                }
        
        return self.collection.insert_one(user)


    def find_user_by_email(self, email):
        return self.collection.find_one({"email": email})
    
    def get_user_id_by_email(self, email):
        user = self.collection.find_one({"email": email}) 
        if user:
            return user["user_id"]
        return None

    def validate_password(self, email, password):
        user = self.find_user_by_email(email)
        if user and check_password_hash(user["password"], password):
            return user
        return None
    
    def find_user_by_id(self, user_id):
        return self.collection.find_one({"user_id": user_id})
    
class ClientModel:
    def __init__(self, db):
        self.collection = db.clients

    def create_client(self, email, password, org_name, admin_name, client_type):
        hashed_password = generate_password_hash(password)
        client_id = str(uuid.uuid4()) 
        client = {
                    "client_id": client_id, 
                    "email": email,
                    "password": hashed_password,
                    "roles": ["client"],
                    "org_name": org_name,
                    "client_type": client_type,
                    "admin_name": admin_name
                }
        
        return self.collection.insert_one(client)


    def find_client_by_email(self, email):
        return self.collection.find_one({"email": email})
    
    def get_client_id_by_email(self, email):
        client = self.collection.find_one({"email": email}) 
        if client:
            return client["client_id"]
        return None

    def validate_password(self, email, password):
        client = self.find_client_by_email(email)
        if client and check_password_hash(client["password"], password):
            return client
        return None
    
class UserProfileModel:

    def __init__(self, db):
        self.collection = db.user_profile_data

    def get_profiles_by_user(self, user_id):
        return list(self.collection.find({"user_id": user_id},  {"_id": 0, "profile_id": 1, "user_id": 1, "profile_name": 1, "profile_data": 1}))

    def create_profile(self, user_id, profile_id, profile_name, profile_data):
        print("here 2...", user_id, profile_id, profile_name, profile_data)
        profile = {
            "user_id": user_id,
            "profile_id": profile_id,
            "profile_name": profile_name,
            "profile_data": profile_data,
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
        }
        return self.collection.insert_one(profile)

    def update_profile(self, profile_id, user_id, profile_name, profile_data):
        return self.collection.update_one(
            {"profile_id": profile_id, "user_id": user_id},
            {
                "$set": {
                    "profile_name": profile_name,
                    "profile_data": profile_data,
                    "updated_at": datetime.now(),
                }
            },
        )

    def delete_profile(self, profile_id, user_id):
        return self.collection.delete_one({"profile_id": profile_id, "user_id": user_id})

    def find_records_by_user(self, user_id):
        return list(self.collection.find({"user_id": user_id}))
    

class UserProfileMappingModel:

    def __init__(self, db):
        self.collection = db.user_profile_mapping
    
    def create_user_profile_mapping(self, user_id, data):
        record = {
            "user_id": user_id,
            "profile_id": data["profile_id"],
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
        return self.collection.insert_one(record)

    def get_profiles_by_user_id(self, user_id):

        profiles = self.collection.find({"user_id": user_id}, {"_id": 0, "profile_id": 1})
        profile_list = list()
        for p in profiles:
            profile_list.append(p["profile_id"])

        return profile_list