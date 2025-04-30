from app.controllers.auth_controller import register_user, login_user, refresh_token
from app.controllers.data_controller import healthcheck, get_profiles, create_profile, edit_profile, get_user_custom_requests
from app.controllers.data_controller import  delete_profile, get_user_requests, update_request_status, get_user_dashboard_summary, update_custom_request_status
from app.controllers.data_controller import get_user_dashboard_analytics
from app.controllers.auth_controller import register_vendor, vendor_login
from app.controllers.vendor_controller import get_vendor_requests, vendor_fetch_user_data, download_approved_data, create_data_request_from_dashboard_custom
from app.controllers.vendor_controller import get_vendor_dashboard_summary, get_vendor_requests_table, create_data_request_from_dashboard
from app.controllers.vendor_controller import get_vendor_custom_requests, get_vendor_details, update_vendor_details, get_vendor_dashboard_analytics

def register_routes(app):

    # Healthcheck
    app.add_url_rule("/api/health", view_func=healthcheck, methods=["GET"])

    # API for User Dashboard Summary
    app.add_url_rule("/api/user/dashboard-summary", view_func=get_user_dashboard_summary, methods=["GET"])

    # User

    # Authentication Routes
    app.add_url_rule("/api/auth/register", view_func=register_user, methods=["POST"])
    app.add_url_rule("/api/auth/login", view_func=login_user, methods=["POST"])
    app.add_url_rule("/api/auth/refresh", view_func=refresh_token, methods=["POST"])

    # GET Profiles
    app.add_url_rule("/api/user/profiles", view_func=get_profiles, methods=["GET"])
    # POST Create Profile
    app.add_url_rule("/api/user/profiles", view_func=create_profile, methods=["POST"])
    # PUT Edit Profile
    app.add_url_rule("/api/user/profiles", view_func=edit_profile, methods=["PUT"])
    # DELETE Profile
    app.add_url_rule("/api/user/profiles", view_func=delete_profile, methods=["DELETE"])
    # Get vendor requests made for a specific user
    # app.add_url_rule("/api/user/vendor-requests", view_func=get_requests_for_user, methods=["GET"])

    # Vendor

    # Vendor registration
    app.add_url_rule("/api/vendor/register", view_func=register_vendor, methods=["POST"])
    # Vendor login
    app.add_url_rule("/api/vendor/login", view_func=vendor_login, methods=["POST"])
    # Vendor AUth Refresh token
    app.add_url_rule("/api/auth/refresh", view_func=refresh_token, methods=["POST"])
    # Vendor Fetch User Profile API
    # app.add_url_rule("/api/vendor/fetch-user", view_func=fetch_user_profile, methods=["POST"])

    # Get vendor request logs
    app.add_url_rule("/api/vendor/logs", view_func=get_vendor_requests, methods=["GET"])

    # API for Vendor Dashboard Summary
    app.add_url_rule("/api/vendor/dashboard-summary", view_func=get_vendor_dashboard_summary, methods=["GET"])

    # API for Vendor Requests Table
    app.add_url_rule("/api/vendor/requests-table", view_func=get_vendor_requests_table, methods=["GET"])

    # Vendor requests user data (creates pending request)
    app.add_url_rule("/api/vendor/fetch-user", view_func=vendor_fetch_user_data, methods=["POST"])

    # User actions
    app.add_url_rule("/api/user/requests", view_func=get_user_requests, methods=["GET"])

    # API for Users to Fetch Custom Requests
    app.add_url_rule("/api/user/custom-requests", view_func=get_user_custom_requests, methods=["GET"])

    app.add_url_rule("/api/user/request/approve", view_func=update_request_status, methods=["PUT"])

    # Vendor actions
    app.add_url_rule("/api/vendor/requests", view_func=get_vendor_requests, methods=["GET"])

    # Vendor downloads approved data
    app.add_url_rule("/api/vendor/download-approved", view_func=download_approved_data, methods=["POST"])
    
    #request user data from dashboard
    app.add_url_rule("/api/vendor/request-data-dashboard", view_func=create_data_request_from_dashboard, methods=["POST"])

    #request user Custom data from dashboard
    app.add_url_rule("/api/vendor/request-data-dashboard-custom", view_func=create_data_request_from_dashboard_custom, methods=["POST"])

    # API for Vendor Custom Requests Table
    app.add_url_rule("/api/vendor/custom-requests", view_func=get_vendor_custom_requests, methods=["GET"])

    # API for UPDATE CUSTOM Custom Requests Table
    app.add_url_rule("/api/user/custom-requests/approve", view_func=update_custom_request_status, methods=["POST"])

    app.add_url_rule("/api/vendor/details", view_func=get_vendor_details, methods=["GET"])

    app.add_url_rule("/api/vendor/details", view_func=update_vendor_details, methods=["PUT"])

    app.add_url_rule("/api/user/analytics", view_func=get_user_dashboard_analytics, methods=["GET"])
    
    app.add_url_rule("/api/vendor/analytics", view_func=get_vendor_dashboard_analytics, methods=["GET"])