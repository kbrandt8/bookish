from threading import Thread, Lock

from flask import Blueprint, render_template, redirect, url_for, flash
from flask import current_app
from flask_login import LoginManager, login_required, login_user, current_user, logout_user

from book_shelf import BookShelf
from .forms import LoginForm, RegisterForm, UploadForm
from .models import User, db, UserBook
from .services.user_service import register_new_user, validate_login, add_user_books

views = Blueprint('views', __name__)
thread_lock = Lock()
RESULTS = []
login_manager = LoginManager()


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
        user = validate_login(form.email.data.lower(), form.password.data)
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
        user = current_user.id
        app = current_app._get_current_object()

        def run_add_recs():
            with app.app_context():
                add_user_books(user,form)

        Thread(target=run_add_recs).start()


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
