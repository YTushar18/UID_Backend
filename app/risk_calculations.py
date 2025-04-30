from flask import current_app
from app.email_utils import send_email  # your existing Mailgun sender

def update_vendor_risk_score(vendor_id, new_status):
    db = current_app.db

    # Determine the score delta
    if new_status == "Approved":
        delta = -5
    elif new_status == "Rejected":
        delta = +1
    elif new_status == "Malicious":
        delta = +5
    else:
        return 

    # Update vendor's risk_score
    vendor = db.vendors.find_one_and_update(
        {"vendor_id": vendor_id},
        {"$inc": {"risk_score": delta}},
        return_document=True
    )

    if not vendor:
        print("Vendor not found while updating risk score.")
        return

    risk_score = vendor.get("risk_score", 0)
    if risk_score >= 50:

        subject = "⚠️ Warning: High Risk Score on Universal Identity Nexus"
        message = f"""
                        Hello {vendor['vendor_name']},

                        Your account has received multiple data request flags from users.

                        Current Risk Score: {risk_score}

                        This is a warning. Continued reports may result in temporary suspension or permanent restriction of your access.

                        Please review your request activity and adjust accordingly.

                        — Universal Identity Nexus Trust & Safety Team
        """

        send_email(vendor["admin_contact"], subject, message)