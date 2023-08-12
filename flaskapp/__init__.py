from flask import Flask
from config import Config
from dash import Dash
from flask.helpers import get_root_path


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    register_extensions(app)
    register_blueprints(app)
    register_dashapp(app)

    return app


def register_extensions(app):
    from flaskapp.extensions import db
    from flaskapp.extensions import migrate

    db.init_app(app)
    migrate.init_app(app, db)


def register_blueprints(app):
    from flaskapp.views.home import home

    app.register_blueprint(home)


def register_dashapp(app):
    from flaskapp.dashapp.layout import layout
    from flaskapp.dashapp.callbacks import register_callbacks

    # Meta tags for viewport responsiveness
    meta_viewport = {
        "name": "viewport", "content": "width=device-width, initial-scale=1, shrink-to-fit=no"}

    dashapp = Dash(
        __name__,
        server=app,
        url_base_pathname='/dashboard/',
        assets_folder=get_root_path(__name__) + '/dashboard/assets/',
        meta_tags=[meta_viewport]
    )

    with app.app_context():
        dashapp.layout = layout
        register_callbacks((dashapp))
