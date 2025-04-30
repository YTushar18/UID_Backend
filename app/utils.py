from werkzeug.security import generate_password_hash, check_password_hash
import requests
import os
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

def send_email(to_email, subject, content):
    MAILGUN_DOMAIN="sandboxb5e2c70ddbfa43f9909634934cdeb4a1.mailgun.org"
    MAILGUN_API_KEY="4cfde503502c46e32f58247395e778cb-17c877d7-08ee0b55"

    return requests.post(
        f"https://api.mailgun.net/v3/{MAILGUN_DOMAIN}/messages",
        auth=("api", MAILGUN_API_KEY),
        data={
            "from": f"Universal Identity Nexus <mailgun@{MAILGUN_DOMAIN}>",
            "to": [to_email],
            "subject": subject,
            "text": content
        }
    )