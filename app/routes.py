from app.controllers.auth_controller import register_user, login_user, refresh_token
from app.controllers.data_controller import get_records, get_user_profile_mapping, get_profiles
from app.controllers.data_controller import get_profiles, create_profile, edit_profile, delete_profile

def register_routes(app):

    # Healthcheck
    app.add_url_rule("/api/healthcheck", view_func=get_records, methods=["GET"])

    # Authentication Routes
    app.add_url_rule("/api/auth/register", view_func=register_user, methods=["POST"])
    app.add_url_rule("/api/auth/login", view_func=login_user, methods=["POST"])
    app.add_url_rule("/api/auth/refresh", view_func=refresh_token, methods=["POST"])

    # Protected Data Routes
    app.add_url_rule("/api/data", view_func=get_records, methods=["GET"])

    app.add_url_rule( "/api/user/profile-mapping", view_func=get_user_profile_mapping, methods=["GET"])

    # GET Profiles
    app.add_url_rule("/api/user/profiles", view_func=get_profiles, methods=["GET"])
    # POST Create Profile
    app.add_url_rule("/api/user/profiles", view_func=create_profile, methods=["POST"])
    # PUT Edit Profile
    app.add_url_rule("/api/profiles", view_func=edit_profile, methods=["PUT"])
    # DELETE Profile
    app.add_url_rule("/api/profiles", view_func=delete_profile, methods=["DELETE"])