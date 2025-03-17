from bson import ObjectId
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import uuid

class UserModel:
    def __init__(self, db):
        self.collection = db.users

    def create_user(self, email, username, password, first_name, last_name):
        hashed_password = generate_password_hash(password)
        user_id = str(uuid.uuid4()) 
        user = {
                    "user_id": user_id, 
                    "email": email,
                    "password": hashed_password,
                    "username": username,
                    "roles": ["user"],
                    "first_name": first_name,
                    "last_name": last_name,
                }
        
        return self.collection.insert_one(user)

    def find_user_by_username(self, username):
        return self.collection.find_one({"username": username})

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
    
import secrets
from datetime import datetime

class VendorModel:
    def __init__(self, db):
        self.collection = db.vendors

    def find_vendor_by_email(self, email):
        return self.collection.find_one({"admin_contact": email})

    def create_vendor(self, vendor_name, website_url, admin_name, admin_contact_phone, client_type, admin_contact, password):
        vendor_id = secrets.token_hex(8)  # Generate a unique vendor_id
        hashed_password = generate_password_hash(password)  # Hash the password
        api_key = secrets.token_hex(32)   # Generate a secure API key

        vendor_data = {
            "vendor_id": vendor_id,
            "vendor_name": vendor_name,
            "website_url": website_url,
            "admin_name": admin_name,
            "admin_contact_phone": admin_contact_phone,
            "client_type": client_type,
            "admin_contact": admin_contact,  # Admin Email
            "password": hashed_password,  # Hashed Password
            "vendor_api_key": api_key,  # Unique API Key
            "created_at": datetime.utcnow(),
        }
        
        self.collection.insert_one(vendor_data)
        return vendor_data  # Return vendor details, including API key

    def validate_vendor_credentials(self, email, password):
        vendor = self.collection.find_one({"admin_contact": email})
        if vendor and check_password_hash(vendor["password"], password):
            return vendor  # Vendor authenticated
        return None
    
    def validate_vendor_api_key(self, api_key):
        return self.collection.find_one({"vendor_api_key": api_key}, {"_id": 0, "vendor_id": 1, "vendor_name": 1})
    
class ProfileModel:

    def __init__(self, db):
        self.collection = db.user_profile_data

    def get_profiles_by_user(self, user_id):
        return list(self.collection.find({"user_id": user_id}))

    def get_profile_by_name(self, user_id, profile_name):
        return self.collection.find_one({"user_id": user_id, "profile_name": profile_name})

    def create_profile(self, user_id, profile_name, profile_data):
        profile = {
            "user_id": user_id,
            "profile_name": profile_name,
            "profile_data": profile_data,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }
        return self.collection.insert_one(profile)

    def update_profile(self, user_id, profile_name, profile_data):
        return self.collection.update_one(
            {"user_id": user_id, "profile_name": profile_name},
            {
                "$set": {
                    "profile_data": profile_data,
                    "updated_at": datetime.utcnow(),
                }
            }
        )

    def delete_profile(self, user_id, profile_name):
        return self.collection.delete_one({"user_id": user_id, "profile_name": profile_name}) 


class UserApprovalRequestModel:
    def __init__(self, db):
        self.collection = db.user_approval_requests

    def create_request(self, vendor_id, vendor_name, website_url, user_id, profile_name, comments):
        request_entry = {
            "vendor_id": vendor_id,
            "vendor_name": vendor_name,
            "website_url": website_url,
            "user_id": user_id,
            "profile_name": profile_name,
            "comments": comments,
            "status": "Pending",
            "timestamp": datetime.utcnow()
        }
        self.collection.insert_one(request_entry)

    def get_requests_for_user(self, user_id):
        requests = list(self.collection.find(
            {"user_id": user_id},
            {"_id": 1, "vendor_id": 1, "vendor_name": 1, "profile_name": 1, "status": 1, "timestamp": 1}
        ))

        # Convert ObjectId to string
        for req in requests:
            req["_id"] = str(req["_id"])

        return requests

    def get_requests_for_vendor(self, vendor_id):
        return list(self.collection.find({"vendor_id": vendor_id}, {"_id": 1, "user_id": 1, "profile_name": 1, "status": 1, "timestamp": 1}))

    def update_request_status(self, request_id, user_id, status):
        return self.collection.update_one({"_id": ObjectId(request_id), "user_id": user_id}, {"$set": {"status": status}}).modified_count > 0

    def get_request_by_id(self, request_id):
        return self.collection.find_one({"_id": ObjectId(request_id)})
    


from datetime import datetime

class CustomRequestModel:
    def __init__(self, db):
        self.collection = db.custom_requests  # New MongoDB Collection

    def create_custom_request(self, vendor_id, vendor_name, website_url, user_id, custom_fields, comments):
        request_data = {
            "vendor_id": vendor_id,
            "vendor_name": vendor_name,
            "website_url": website_url,
            "user_id": user_id,
            "custom_fields": custom_fields,
            "comments": comments,
            "status": "Pending",
            "timestamp": datetime.utcnow()
        }
        return self.collection.insert_one(request_data)