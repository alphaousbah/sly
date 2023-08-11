from flask import Flask
from config import Config


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    register_extensions(app)
    register_blueprints(app)

    return app


def register_extensions(app):
    from flaskapp.extensions import db
    from flaskapp.extensions import migrate

    db.init_app(app)
    migrate.init_app(app, db)


def register_blueprints(app):
    from flaskapp.views.home import home

    app.register_blueprint(home)
