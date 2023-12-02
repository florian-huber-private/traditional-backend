from flask import Blueprint, request, session, jsonify
from app.extensions import db
from app.models import Category
from app.decorators import login_required

categories_bp = Blueprint("categories", __name__)


@categories_bp.route("/", methods=["GET"])
@login_required
def get_all_categories():
    user_id = session.get("user_id")
    categories = Category.query.filter_by(user_id=user_id).all()
    return jsonify([category.to_dict() for category in categories]), 200


@categories_bp.route("/", methods=["POST"])
@login_required
def create_category():
    user_id = session.get("user_id")
    data = request.get_json()
    name = data.get("name")

    if not name:
        return jsonify({"error": "Category name is required"}), 400

    existing_category = Category.query.filter_by(name=name, user_id=user_id).first()
    if existing_category:
        return jsonify({"error": "A category with this name already exists"}), 409

    new_category = Category(name=name, user_id=user_id)
    db.session.add(new_category)
    db.session.commit()

    return (
        jsonify({"message": "Category created", "category": new_category.to_dict()}),
        201,
    )


@categories_bp.route("/<int:category_id>", methods=["GET"])
@login_required
def get_category(category_id):
    user_id = session.get("user_id")
    category = Category.query.filter_by(id=category_id, user_id=user_id).first()

    if category is None:
        return jsonify({"error": "Category not found"}), 404

    return jsonify(category.to_dict()), 200


@categories_bp.route("/<int:category_id>", methods=["PUT"])
@login_required
def update_category(category_id):
    user_id = session.get("user_id")
    category = Category.query.filter_by(id=category_id, user_id=user_id).first()

    if category is None:
        return jsonify({"error": "Category not found"}), 404

    data = request.get_json()
    category.name = data.get("name", category.name)
    db.session.commit()

    return jsonify({"message": "Category updated", "category": category.to_dict()}), 200


@categories_bp.route("/<int:category_id>", methods=["DELETE"])
@login_required
def delete_category(category_id):
    user_id = session.get("user_id")
    category = Category.query.filter_by(id=category_id, user_id=user_id).first()

    if category is None:
        return jsonify({"error": "Category not found"}), 404

    db.session.delete(category)
    db.session.commit()

    return jsonify({"message": "Category deleted"}), 200
