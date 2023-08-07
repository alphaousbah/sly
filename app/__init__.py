from flask import Flask


def create_app():
    server = Flask(__name__)
    server.config.from_object('deployment.development')

    register_extensions(server)
    register_blueprints(server)

    return server


def register_extensions(app):
    from app.extensions import db, migrate

    db.init_app(app)
    migrate.init_app(app)


def register_blueprints(server):
    from app.views.home import home

    server.register_blueprint(home)
