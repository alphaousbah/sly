from flask import Flask
from config import BaseConfig


def create_app():
    app = Flask(__name__)
    app.config.from_object(BaseConfig)

    register_extensions(app)
    register_blueprints(app)

    return app


def register_extensions(app):
    from app.extensions import db, migrate

    db.init_app(app)
    migrate.init_app(app)


def register_blueprints(app):
    from app.views.home import home

    app.register_blueprint(home)
