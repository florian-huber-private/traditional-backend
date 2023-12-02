from flask import Flask
from flask_session import Session
from flask_cors import CORS
from app.extensions import db
from app.auth.routes import auth_bp
from app.user.routes import user_bp
from app.tasks.routes import tasks_bp
from app.categories.routes import categories_bp


def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "your_secret_key"
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///tasklist.db"
    app.config["SESSION_TYPE"] = "sqlalchemy"
    app.config["SESSION_SQLALCHEMY"] = db

    app.config["SESSION_COOKIE_SECURE"] = True
    app.config["SESSION_COOKIE_SAMESITE"] = "None"

    sess = Session(app)

    db.init_app(app)
    with app.app_context():
        db.create_all()

    CORS(app, supports_credentials=True)

    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(user_bp, url_prefix="/user")
    app.register_blueprint(tasks_bp, url_prefix="/tasks")
    app.register_blueprint(categories_bp, url_prefix="/categories")

    return app
