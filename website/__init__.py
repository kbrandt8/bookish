from flask import Flask
from flask_bootstrap import Bootstrap5
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = ''
    Bootstrap5(app)
    from .views import views
    app.register_blueprint(views, url_prefix='/')
    return app
