from flask import Blueprint, request, session, jsonify
from app.extensions import db
from app.models import User
from app.utils import validate_email, validate_password
from app.decorators import login_required

user_bp = Blueprint("user", __name__)


@user_bp.route("/profile", methods=["GET"])
@login_required
def get_user():
    user_id = session.get("user_id")
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify(user.to_dict()), 200


@user_bp.route("/profile/update", methods=["PUT"])
@login_required
def update_user():
    user_id = session.get("user_id")
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    data = request.get_json()
    username = data.get("username")
    email = data.get("email")

    if username and username != user.username:
        if User.query.filter_by(username=username).first():
            return jsonify({"error": "Username already taken"}), 409
        user.username = username

    if email and email != user.email:
        is_valid_email, email_message = validate_email(email)
        if not is_valid_email:
            return jsonify({"error": email_message}), 400
        if User.query.filter_by(email=email).first():
            return jsonify({"error": "Email already taken"}), 409
        user.email = email

    db.session.commit()
    return jsonify({"message": "Profile updated", "user": user.to_dict()}), 200


@user_bp.route("/profile/update/password", methods=["PUT"])
@login_required
def update_user_password():
    user_id = session.get("user_id")
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    data = request.get_json()
    old_password = data.get("old_password")
    new_password = data.get("new_password")

    if not user.check_password(old_password):
        return jsonify({"error": "Incorrect old password"}), 401

    is_valid_password, password_message = validate_password(new_password)
    if not is_valid_password:
        return jsonify({"error": password_message}), 400

    user.set_password(new_password)
    db.session.commit()
    return jsonify({"message": "Password updated"}), 200


@user_bp.route("/profile/delete", methods=["DELETE"])
@login_required
def delete_user():
    user_id = session.get("user_id")
    user = User.query.get(user_id)

    if not user:
        return jsonify({"error": "User not found"}), 404

    db.session.delete(user)
    db.session.commit()

    session.pop("user_id", None)

    return jsonify({"message": "User account deleted successfully"}), 200
