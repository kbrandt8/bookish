import json
from threading import Thread, Lock

from flask import Blueprint, render_template, redirect, url_for,flash
from flask import current_app
from flask_login import LoginManager, login_required, login_user, current_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash

from book_shelf import BookShelf
from user_info import UserInfo
from .forms import LoginForm, RegisterForm, UploadForm
from .models import User, db, Book, Subject, UserBook,UserSubject
from .services.user_service import register_new_user, validate_login

views = Blueprint('views', __name__)
thread_lock = Lock()
RESULTS = []
login_manager = LoginManager()


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


def get_user_info(user_id,filename, story_graph=False, good_reads=False):
    user = UserInfo()
    shelf = BookShelf(user_id)
    if story_graph:
        user.story_graph_csv(filename)
    if good_reads:
        user.good_reads_csv(filename)
    books = user.all_books
    for book in books:
        shelf.book_info(book)
    return shelf.owned_books

def add_books(user_id, books, read):
    user = User.query.get(user_id)
    if not user:
        print(f"User ID {user_id} not found.")
        return

    for book_data in books:
        title = book_data['Title']
        author = book_data['Author']
        link = f"https://openlibrary.org{book_data['Key']}"
        shared_subjects = book_data.get('Subjects', [])

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
            user_book = UserBook(user_id=user.id, book_id=book.id, is_read=read)
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
        success = register_new_user(form)
        if success:
            return redirect(url_for('views.login'))
        else:
            flash("Email already exists")
    return render_template("register.html", form=form)


@views.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = validate_login(form.email.data.lower(),form.password.data)
        if user:
            login_user(user)
            return redirect(url_for('views.account'))
        else:
            flash("Please check credentials!")

    return render_template("login.html", form=form)


@views.route("/start_search")
@login_required
def start_task():
    user = current_user.id
    app = current_app._get_current_object()

    def run_add_recs():
        with app.app_context():
            shelf = BookShelf(user)
            shelf.books_from_subjects()

    thread = Thread(target=run_add_recs)
    thread.start()
    return render_template("loading.html")


@views.route("/recommendations")
@login_required
def recommendations():
    books = db.session.execute(db.select(UserBook).where(
        UserBook.user_id == current_user.id,
        UserBook.is_read == False,
        UserBook.is_recommended == True
    )).scalars().all()
    return render_template("recommendations.html", result=books)


@views.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = UploadForm()
    if form.validate_on_submit():
        file = form.file.data
        file_name = "user_data.csv"
        file.save(file_name)
        story_graph = True if form.data_type.data == "sg" else False
        good_reads = True if form.data_type.data == "gr" else False
        user = current_user.id
        app = current_app._get_current_object()

        def run_add_recs():
            with app.app_context():
                user_books = get_user_info(user,file_name, story_graph=story_graph, good_reads=good_reads)
                print("Finished books")
                add_books(user, user_books, True)
                print("books added")

        thread = Thread(target=run_add_recs)
        thread.start()

    return render_template("account.html", form=form)


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
def book_actions(book_id, action):
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
    elif action == "not_recommended":
        user_book.is_recommended = False
    elif action == "recommended":
        user_book.is_recommended = True
    else:
        return redirect(url_for("views.recommendations"))

    db.session.commit()
    return redirect(url_for("views.recommendations"))
