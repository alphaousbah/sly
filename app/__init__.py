from flask import Flask
from config import BaseConfig


def create_app():
    server = Flask(__name__)
    server.config.from_object(BaseConfig)

    server.config.update(
        SQLALCHEMY_DATABASE_URI=server.config.get('SQLALCHEMY_DATABASE_URI'),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
    )

    register_extensions(server)
    register_blueprints(server)

    return server


def register_extensions(server):
    from app.extensions import db
    from app.extensions import migrate

    db.init_app(server)
    migrate.init_app(server, db)


def register_blueprints(server):
    from app.views.home import home

    server.register_blueprint(home)
