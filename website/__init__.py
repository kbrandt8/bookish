import os

from dotenv import load_dotenv
from flask import Flask
from flask_wtf.csrf import CSRFProtect
from flask_bootstrap import Bootstrap5
from flask_wtf import FlaskForm
from flask_cors import CORS
from flask_login import LoginManager
from sqlalchemy.orm import DeclarativeBase
from .views import views

from .models import User, Book, db,Subject,UserBook


class Base(DeclarativeBase):
    pass


def create_app():
    app = Flask(__name__)
    load_dotenv()
    app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("SQLDB")
    app.secret_key = os.getenv('SECRET_KEY')

    db.init_app(app)
    CORS(app)
    csrf = CSRFProtect(app)
    login_manager = LoginManager()
    login_manager.init_app(app)

    Bootstrap5(app)

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    app.register_blueprint(views, url_prefix='/')
    return app
