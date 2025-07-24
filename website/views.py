from threading import Thread

from flask import Blueprint, render_template, redirect, url_for, flash
from flask import current_app
from flask_login import LoginManager, login_required, login_user, current_user, logout_user
from flask_wtf.csrf import generate_csrf

from book_shelf import BookShelf
from .forms import LoginForm, RegisterForm, UploadForm
from .models import User, db, UserBook
from .services.user_service import register_new_user, validate_login, add_user_books

views = Blueprint('views', __name__)
login_manager = LoginManager()


def run_in_thread(func):
    app = current_app._get_current_object()

    def wrapped():
        with app.app_context():
            func()

    Thread(target=wrapped).start()


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, user_id)


@views.route("/")
def home():
    return render_template("index.html")


@views.route("/browse", methods=["GET"])
def browse():
    query = request.args.get("q", "").strip()
    books = []
    csrf_token = generate_csrf()
    shelf = BookShelf()

    if query:
        try:
            books = shelf.search_openlibrary_books(query)
        except RuntimeError as e:
            flash(str(e))

    return render_template("browse.html", books=books, query=query, csrf_token=csrf_token)


from flask import request


@views.route("/add_openlibrary_book", methods=["POST"])
@login_required
def add_openlibrary_book():
    title = request.form.get("title")
    author = request.form.get("author")
    is_recommended = request.form.get("is_recommended") != "False"
    is_read = request.form.get("is_read") == "True"
    if not (title and author):
        flash("Missing title or author.")
        return redirect(url_for("views.browse"))
    shelf = BookShelf()
    shelf.add_open_library_book(current_user.id, request.form)
    msg = f"📚 '{title}' added"

    if is_read:
        msg += " and marked as read ✅"
    elif not is_recommended:
        msg += " — we'll show fewer like this 💔"
    else:
        msg += " to your watchlist ➕"

    flash(msg)
    return redirect(url_for("views.browse", q=request.args.get("q", "")))


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
    run_in_thread(lambda: BookShelf().books_from_subjects(user))
    return render_template("loading.html")


@views.route("/books/<state>")
@login_required
def books(state):
    is_read = (state == "read")
    books = db.session.execute(
        db.select(UserBook)
        .where(
            UserBook.user_id == current_user.id,
            UserBook.is_read == is_read,
            UserBook.is_recommended == True
        )
        .options(db.joinedload(UserBook.book))
    ).scalars().all()
    return render_template(
        "books.html",
        result=books,
        csrf_token=generate_csrf(),
        is_read=is_read,
        state=state
    )


@views.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = UploadForm()
    if form.validate_on_submit():
        user = current_user.id
        run_in_thread(lambda: add_user_books(user, form))
        flash("Books are being processed...")
    return render_template("account.html", form=form)


@views.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('views.home'))


@views.route("/batch_book_action/<state>", methods=["POST"])
@login_required
def batch_book_action(state):
    book_ids = request.form.getlist("book_ids")
    action = request.form.get("action")

    if not book_ids or not action:
        flash("No books selected or invalid action.", "warning")
        return redirect(url_for("views.watchlist", state=state))

    for book_id in book_ids:
        user_book = UserBook.query.filter_by(user_id=current_user.id, book_id=book_id).first()
        if not user_book:
            continue

        if action == "delete":
            db.session.delete(user_book)
        elif action == "mark_read":
            user_book.is_read = True
        elif action == "not_recommended":
            user_book.is_recommended = False

    db.session.commit()
    flash("Batch update successful!", "success")
    return redirect(url_for("views.books", state=state))
