from flask import Blueprint, request, session, jsonify
from datetime import datetime
from app.extensions import db
from app.models import Task, TaskPriority, TaskStatus, Category
from app.utils import (
    validate_due_date,
    validate_categories,
    validate_priority,
    validate_status,
)
from app.decorators import login_required


tasks_bp = Blueprint("tasks", __name__)


@tasks_bp.route("/", methods=["GET"])
@login_required
def get_all_tasks():
    user_id = session.get("user_id")
    tasks = Task.query.filter_by(user_id=user_id).all()
    return jsonify([task.to_dict() for task in tasks]), 200


@tasks_bp.route("/", methods=["POST"])
@login_required
def create_task():
    user_id = session.get("user_id")
    data = request.get_json()

    title = data.get("title")
    if not title:
        return jsonify({"error": "Title is required."}), 400

    description = data.get("description", "")

    is_valid, priority = validate_priority(
        data.get("priority", TaskPriority.MEDIUM.name)
    )
    if not is_valid:
        return (
            jsonify({"error": priority}),
            400,
        )

    is_valid, categories = validate_categories(data.get("categories", []), user_id)
    if not is_valid:
        return (
            jsonify({"error": categories}),
            400,
        )

    is_valid, due_date = validate_due_date(data.get("due_date"))
    if not is_valid:
        return (
            jsonify({"error": due_date}),
            400,
        )

    new_task = Task(
        user_id=user_id,
        title=title,
        description=description,
        priority=priority,
        categories=categories,
        due_date=due_date,
    )

    db.session.add(new_task)
    db.session.commit()

    return jsonify({"message": "Task created", "task": new_task.to_dict()}), 201


@tasks_bp.route("/<int:task_id>", methods=["GET"])
@login_required
def get_task(task_id):
    user_id = session.get("user_id")
    task = Task.query.filter_by(id=task_id, user_id=user_id).first()

    if task is None:
        return jsonify({"error": "Task not found"}), 404

    return jsonify(task.to_dict()), 200


@tasks_bp.route("/<int:task_id>", methods=["PUT"])
@login_required
def update_task(task_id):
    user_id = session.get("user_id")
    task = Task.query.filter_by(id=task_id, user_id=user_id).first()

    if task is None:
        return jsonify({"error": "Task not found"}), 404

    data = request.get_json()

    task.title = data.get("title", task.title)
    if not task.title:
        return jsonify({"error": "Title is required."}), 400

    task.description = data.get("description", task.description)

    is_valid, priority = validate_priority(data.get("priority", task.priority.name))
    if not is_valid:
        return jsonify({"error": priority}), 400

    is_valid, categories = validate_categories(data.get("categories", []), user_id)
    if not is_valid:
        return jsonify({"error": categories}), 400
    task.categories = categories

    is_valid, due_date = validate_due_date(data.get("due_date"))
    if not is_valid:
        return jsonify({"error": due_date}), 400
    task.due_date = due_date

    is_valid, status = validate_status(data.get("status", task.status.name))
    if not is_valid:
        return jsonify({"error": status}), 400
    task.status = status

    db.session.commit()

    return jsonify({"message": "Task updated", "task": task.to_dict()}), 200


@tasks_bp.route("/<int:task_id>", methods=["DELETE"])
@login_required
def delete_task(task_id):
    user_id = session.get("user_id")
    task = Task.query.filter_by(id=task_id, user_id=user_id).first()

    if task is None:
        return jsonify({"error": "Task not found"}), 404

    db.session.delete(task)
    db.session.commit()

    return jsonify({"message": "Task deleted"}), 200
