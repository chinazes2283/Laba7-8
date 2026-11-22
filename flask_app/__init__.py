from flask import Flask
from flask_migrate import Migrate

from .models import db
from .views import api


def create_app(config=None):
    app = Flask(__name__)
    app.config.update(SQLALCHEMY_DATABASE_URI="sqlite:///library.sqlite3")
    if config:
        app.config.update(config)

    db.init_app(app)
    Migrate(app, db)
    app.register_blueprint(api)
    return app
