import json
from threading import Thread, Lock

from flask import Blueprint, render_template, redirect, url_for
from flask import current_app
from flask_login import LoginManager, login_required, login_user, current_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash

from book_shelf import BookShelf
from user_info import UserInfo
from .forms import LoginForm, RegisterForm
from .models import User, db, Book, Subject, UserBook

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


def get_subjects(user_id):
    user_books = UserBook.query.filter_by(user_id=user_id).all()

    user_subjects = set()

    for user_book in user_books:
        book = user_book.book
        if book:
            for subject in book.subjects:
                user_subjects.add(subject)

    return list(user_subjects)


def get_recs(user, type_of, books=None):
    if books is None:
        books = []
    subjects = get_subjects(user)

    shelf = BookShelf()
    if type_of == "subject":
        shelf.books_from_subjects(subjects)
    elif type_of == "similar":
        shelf.similar_books(books)

    return shelf.recommendations


def get_books():
    with open('recommendations.json', 'r') as f:
        data = json.load(f)
        return data


def add_recs(user_id,type_of):

    recs = get_recs(user_id,type_of)
    user = User.query.get(user_id)
    if not user:
        print(f"User ID {user_id} not found.")
        return

    for book_data in recs:
        title = book_data['title']
        author = book_data['author']
        link = f"https://openlibrary.org{book_data['key']}"
        shared_subjects = book_data.get('shared_subjects', [])

        book = Book.query.filter_by(title=title, author=author).first()
        if not book:
            book = Book(title=title, author=author, link=link)
            db.session.add(book)

        for subject_name in shared_subjects:
            subject = Subject.query.filter_by(name=subject_name).first()
            if not subject:
                subject = Subject(name=subject_name)
                db.session.add(subject)
                db.session.flush()
            if subject not in book.subjects:
                book.subjects.append(subject)

        db.session.flush()

        existing_userbook = UserBook.query.filter_by(user_id=user.id, book_id=book.id).first()
        if not existing_userbook:
            user_book = UserBook(user_id=user.id, book_id=book.id, is_read=False)
            db.session.add(user_book)

    db.session.commit()


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
            new_user = User(email=email, name=name, password=password)
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
        check_password = check_password_hash(user.password, form.password.data)
        if check_password:
            login_user(user)
            return redirect(url_for('views.account'))

    return render_template("login.html", form=form)


@views.route("/start_search/<type_of>")
@login_required
def start_task(type_of):
    user = current_user.id
    app = current_app._get_current_object()
    def run_add_recs():
        with app.app_context():
            add_recs(user,type_of)
    thread = Thread(target=run_add_recs)
    thread.start()
    return render_template("loading.html", result=RESULTS)


@views.route("/recommendations")
@login_required
def recommendations():
    books = db.session.execute(db.select(UserBook).where(UserBook.user_id == current_user.id)).scalars().all()
    if books:
        return render_template("recommendations.html", result=books)
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

@views.route("/api/book_actions/<int:book_id>/<action>", methods=['GET', 'POST'])
@login_required
def book_actions(book_id,action):
    user_book = (
        db.session.query(UserBook)
        .filter_by(book_id=book_id, user_id=current_user.id)
        .first()
    )
    if not user_book:
        return redirect(url_for("views.recommendations"))

    if action == "delete":
        db.session.delete(user_book)
    elif action == "is_read":
        user_book.is_read = True
    elif action == "is_not_read":
        user_book.is_read = False
    else:
        return redirect(url_for("views.recommendations"))


    db.session.commit()
    return redirect(url_for("views.recommendations"))
