from flask import Blueprint, request, session, jsonify
from app.extensions import db
from app.models import User
from app.utils import validate_email, validate_password
from app.decorators import login_required

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")

    if not username or not email or not password:
        return jsonify({"error": "Missing username, email, or password"}), 400

    is_valid_email, email_message = validate_email(email)
    if not is_valid_email:
        return jsonify({"error": email_message}), 400

    is_valid_password, password_message = validate_password(password)
    if not is_valid_password:
        return jsonify({"error": password_message}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({"error": "Username already taken"}), 409
    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Email already taken"}), 409

    new_user = User(username=username, email=email)
    new_user.set_password(password)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "Registration successful"}), 201


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"error": "Missing email or password"}), 400

    user = User.query.filter_by(email=email).first()
    if user and user.check_password(password):
        session["user_id"] = user.id
        return jsonify({"message": "Login successful", "user": user.to_dict()}), 200
    else:
        return jsonify({"error": "Invalid email or password"}), 401


@auth_bp.route("/logout", methods=["POST"])
@login_required
def logout():
    session.pop("user_id", None)
    return jsonify({"message": "Logout successful"}), 200
