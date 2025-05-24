import json
from threading import Thread, Lock

from flask import Blueprint, render_template, redirect, url_for
from flask_login import LoginManager, login_required,login_user,current_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash

from book_shelf import BookShelf
from user_info import UserInfo

from .forms import LoginForm, RegisterForm
from .models import User,db

views = Blueprint('views', __name__)
thread_lock = Lock()
RESULTS = []
login_manager = LoginManager()


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


def get_user_info(story_graph=False, good_reads=False):
    user = UserInfo()
    if story_graph:
        user.story_graph_csv("story_graph.csv")
    if good_reads:
        user.good_reads_csv("goodreads_library_export.csv")
    return user


def get_subjects(type_of):
    with open('recommendations.json', 'r') as f:
        data = json.load(f)
        return data['subjects']


def get_recs(type_of):
    subjects = get_subjects(type_of)
    with Thread:
        global RESULTS
        shelf = BookShelf()
        shelf.books_from_subjects(subjects)
        RESULTS = shelf.recommendations


def add_recs(user, recs):
    pass


@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)


@views.route("/")
def home():
    return render_template("index.html")


@views.route("/register", methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        name = form.name.data
        email = form.email.data
        password = generate_password_hash(form.password.data)
        in_db = User.query.filter_by(email=email).first()
        if not in_db:
            new_user = User(email=email,name=name,password=password)
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for('views.login'))


    return render_template("register.html", form=form)


@views.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        user = User.query.filter_by(email=email).first()
        check_password = check_password_hash(user.password,form.password.data)
        if check_password:
            login_user(user)
            return redirect(url_for('views.account'))

    return render_template("login.html", form=form)


@views.route("/start_search/<type_of>")
def start_task(type_of):
    thread = Thread(target=get_recs, args=type_of)
    thread.start()
    thread.join()
    return render_template("recommendations", result=RESULTS)


@views.route("/search/<search_type>")
@login_required
def search(search_type):
    return render_template("search.html", type=search_type)


@views.route("/recommendations")
@login_required
def recommendations():
    global RESULTS
    if RESULTS:
        return render_template("results.html", result=RESULTS)
    else:
        return render_template("loading.html")


@views.route("/account")
@login_required
def account():
    return render_template("account.html")


@views.route("/watchlist")
@login_required
def watchlist():
    return render_template("watchlist.html")


@views.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('views.home'))
