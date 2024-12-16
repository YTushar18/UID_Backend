from werkzeug.security import generate_password_hash, check_password_hash
import secrets

def hash_password(password):
    return generate_password_hash(password)

def verify_password(password, hashed):
    return check_password_hash(hashed, password)


def generate_secret_key():
    # Generate a 32-byte secret key
    secret_key = secrets.token_hex(32)
    print(f"SECRET_KEY: {secret_key}")
    return secret_key
