from app.extensions import db
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import enum


class TaskStatus(enum.Enum):
    TODO = "TO_DO"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"


class TaskPriority(enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {"id": self.id, "username": self.username, "email": self.email}


task_categories = db.Table(
    "task_categories",
    db.Column("task_id", db.Integer, db.ForeignKey("task.id"), primary_key=True),
    db.Column(
        "category_id", db.Integer, db.ForeignKey("category.id"), primary_key=True
    ),
)


class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200))
    priority = db.Column(db.Enum(TaskPriority), default=TaskPriority.MEDIUM)
    categories = db.relationship(
        "Category",
        secondary=task_categories,
        lazy="subquery",
        backref=db.backref("tasks", lazy=True),
    )
    creation_date = db.Column(db.DateTime, default=datetime.utcnow)
    due_date = db.Column(db.DateTime)
    status = db.Column(db.Enum(TaskStatus), default=TaskStatus.TODO)

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "title": self.title,
            "description": self.description,
            "priority": self.priority.name,
            "categories": [category.id for category in self.categories],
            "creation_date": self.creation_date.strftime("%Y-%m-%d"),
            "due_date": self.due_date.strftime("%Y-%m-%d") if self.due_date else None,
            "status": self.status.name,
        }


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    def to_dict(self):
        return {"id": self.id, "name": self.name, "user_id": self.user_id}
