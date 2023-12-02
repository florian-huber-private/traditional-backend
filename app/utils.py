import re
from datetime import datetime
from app.models import TaskPriority, Category, TaskStatus


def validate_email(email):
    pattern = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    if re.match(pattern, email):
        return True, email
    return False, "Invalid email format"


def validate_password(password):
    if len(password) < 8:
        return False, "Password must be at least 8 characters"
    if not any(char.isupper() for char in password):
        return False, "Password must contain at least one uppercase letter"
    if not any(char.islower() for char in password):
        return False, "Password must contain at least one lowercase letter"
    if not any(char in "!@#$%^&*()-_=+[{]};:'\",<.>/?\\" for char in password):
        return False, "Password must contain at least one special character"
    return True, password


def validate_due_date(due_date_str):
    if not due_date_str or due_date_str == "":
        return True, None

    try:
        due_date = datetime.strptime(due_date_str, "%Y-%m-%d")
        if due_date < datetime.now():
            return False, "Due date cannot be in the past"
        return True, due_date
    except ValueError:
        return False, "Invalid date format"


def validate_priority(priority_str):
    try:
        priority = TaskPriority[priority_str]
        return True, priority
    except KeyError:
        return False, "Invalid priority value"


def validate_categories(category_ids, user_id):
    if not category_ids:
        return True, []

    categories = Category.query.filter(
        Category.id.in_(category_ids), Category.user_id == user_id
    ).all()

    if len(categories) == len(category_ids):
        return True, categories
    return False, "One or more categories are invalid"


def validate_status(status_str):
    try:
        status = TaskStatus[status_str]
        return True, status
    except KeyError:
        return False, "Invalid status value"
