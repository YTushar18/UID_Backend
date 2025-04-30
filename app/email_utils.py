import os
import json
from flask import current_app
# from flask_mail import Mail, Message
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from app.models import UserModel, VendorModel
from werkzeug.security import generate_password_hash, check_password_hash



def send_email(to, subject, body):
    """
    Function to send an email.
    :param to: Recipient's email address
    :param subject: Subject of the email
    :param body: Body of the email
    """
    import smtplib
    from email.mime.text import MIMEText

    # Create the email
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = 'info@uin.com'
    msg['To'] = to
    try:
        # Connect to the SMTP server
        with smtplib.SMTP('smtp.mailgun.org', 587) as server:
            server.starttls()
            server.login('postmaster@your_domain.com', 'your_password')
            server.sendmail(msg['From'], [msg['To']], msg.as_string())
            print(f"Email sent to {to}")
    except Exception as e:
        print(f"Failed to send email: {e}")
