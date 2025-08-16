from threading import Thread

from flask import Blueprint, render_template, redirect, url_for, flash, jsonify
from flask import current_app
from flask import request
from flask_login import LoginManager, login_required, login_user, current_user, logout_user
from flask_wtf.csrf import generate_csrf

from book_deals import BookDeal
from book_shelf import BookShelf
from .forms import LoginForm, RegisterForm, UploadForm, EmailForm, PasswordForm, NameForm
from .models import User, db, UserBook
from .services.user_service import register_new_user, validate_login, add_user_books, user_book_batch, update_email, \
    update_password, update_name

views = Blueprint('views', __name__)
login_manager = LoginManager()
recommendation_status = {}


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
    if current_user.is_authenticated:
        read = db.session.execute(
            db.select(UserBook)
            .where(
                UserBook.user_id == current_user.id,
                UserBook.is_read == True,
                UserBook.is_recommended == True

            )
        ).scalars().all()
        not_read = db.session.execute(
            db.select(UserBook)
            .where(
                UserBook.user_id == current_user.id,
                UserBook.is_read == False,
                UserBook.is_recommended == True
            )
        ).scalars().all()
        not_read.reverse()
        read.reverse()
        return render_template(
            "index.html",
            results={"read": read, "not_read": not_read})
    return render_template("index.html")


@views.route("/search", methods=["GET"])
def search():
    query = request.args.get("q", "").strip()
    search_type = request.args.get("filter", "q").strip()
    if search_type == "all":
        search_type = "q"
    page = int(request.args.get("page", "1"))
    search_results = {"num_found":0,"books":[]}
    total_pages = 1
    page_range=range(0,1)

    csrf_token = generate_csrf()
    shelf = BookShelf()
    if query:
        try:
            search_results = shelf.search_openlibrary_books(search_type,query,page)
            total_pages = int(int(search_results['num_found'])/100)
            page_min = max(page - 5, 1)
            page_max = min(page + 5, total_pages)
            page_range = range(page_min, page_max + 1)
        except RuntimeError as e:
            flash(str(e))
    return render_template("search.html",
                           search_results=search_results,
                           total_pages=total_pages,
                           query=query,
                           csrf_token=csrf_token,
                           page=page,
                           page_range=page_range,
                           )


@views.route("/add_openlibrary_book", methods=["POST"])
@login_required
def add_openlibrary_book():
    title = request.form.get("title")
    author = request.form.get("author")
    is_recommended = request.form.get("is_recommended") != "False"
    is_read = request.form.get("is_read") == "True"
    if not (title and author):
        flash("Missing title or author.")
        return redirect(url_for("views.search"))
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
    return redirect(url_for("views.search", q=request.args.get("q", "")))


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
            return redirect(url_for('views.home'))
        else:
            flash("Please check credentials!")

    return render_template("login.html", form=form)


@views.route("/get_recs")
@login_required
def get_recs():
    user_id = current_user.id
    app = current_app._get_current_object()
    recommendation_status[user_id] = {"ready": False, "msg": "Initializing...", "progress": 0}
    shelf = BookShelf()
    if not shelf.is_new_user(user_id):
        def run_task():
            with app.app_context():
                try:

                    def update_status(message, progress):
                        print(message)
                        recommendation_status[user_id].update(msg=message, progress=progress)

                    update_status("📚 Analyzing your books...", 10)
                    shelf.sort_subjects(user_id)

                    update_status("📘 Gathering your preferred subjects...", 25)
                    shelf.get_subjects(user_id)

                    update_status("🔍 Searching OpenLibrary by subject...", 50)
                    shelf.search_subjects_bulk()

                    update_status("📊 Sorting your best matches...", 75)
                    shelf.sort_books()

                    update_status("💾 Saving recommendations to your watchlist...", 90)
                    shelf.add_books(user_id)

                    update_status("✅ Complete!", 100)
                    recommendation_status[user_id].update(ready=True)

                except Exception as e:
                    print(f"Error during recommendation task: {e}")
                    recommendation_status[user_id] = {
                        "ready": True,
                        "msg": "An error occurred. Please try again.",
                        "progress": 100
                    }

        Thread(target=run_task).start()
        return render_template("loading.html")
    else:
        flash("Please add books so we can find your recommendations")
        return render_template("search.html")


@views.route("/deals", methods=["GET", "POST"])
@login_required
def deals():
    user = current_user.id
    results = db.session.execute(
        db.select(UserBook)
        .where(
            UserBook.user_id == user,
            UserBook.is_recommended == True,
            UserBook.is_read == False,
            UserBook.deal != None
        )
    ).scalars().all()
    result = sorted(results, key=lambda r: r.deal)
    if request.method == "POST":
        flash("Checking for deals on your unread books!", "success")
        check_deals = db.session.execute(
            db.select(UserBook)
            .where(
                UserBook.user_id == user,
                UserBook.is_recommended == True,
                UserBook.is_read == False,
            ).options(db.joinedload(UserBook.book))
        ).scalars().all()
        run_in_thread(lambda: BookDeal(user, check_deals))
        return render_template("deals.html", result=result, csrf_token=generate_csrf())
    else:
        return render_template("deals.html", result=result, csrf_token=generate_csrf())


@views.route("/recommendation_status")
@login_required
def recommendation_status_check():
    user_id = current_user.id
    status = recommendation_status.get(user_id, {"ready": False, "msg": "Waiting...", "progress": 0})
    return jsonify(status)


@views.route("/results", methods=["POST", "GET"])
@login_required
def results():
    user = current_user.id
    result_books = db.session.execute(
        db.select(UserBook)
        .where(
            UserBook.user_id == user,
            UserBook.is_read == False,
            UserBook.is_recommended == True)
    ).scalars().all()
    return render_template("recommendations.html", results=result_books[-15:])


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
    books.reverse()
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
    user_id = current_user.id
    csv_form = UploadForm()
    email_form = EmailForm()
    password_form = PasswordForm()
    name_form = NameForm()
    form_name = request.form.get("submit")

    if form_name == "Upload" and csv_form.validate_on_submit():
        file = request.files["file"]
        source = request.form.get("data_type")
        run_in_thread(lambda: add_user_books(user_id,file, source))
        flash("Books are being processed...", "info")

    elif form_name == "Update Email" and email_form.validate_on_submit():
        if update_email(user_id, email_form):
            flash("Email updated!", "success")
        else:
            flash("Something went wrong", "danger")

    elif form_name == "Update Password" and password_form.validate_on_submit():
        if update_password(user_id, password_form):
            flash("Password changed successfully.", "success")
        else:
            flash("Something went wrong", "danger")

    elif form_name == "Update Name" and name_form.validate_on_submit():
        if update_name(user_id, name_form):
            flash("Name updated.", "success")
        else:
            flash("Something went wrong", "danger")

    return render_template(
        "account.html",
        csv_form=csv_form,
        email_form=email_form,
        password_form=password_form,
        name_form=name_form
    )


@views.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('views.home'))


@views.route("/batch_book_action/<state>", methods=["POST"])
@login_required
def batch_book_action(state):
    user_id=current_user.id
    book_ids = request.form.getlist("book_ids")
    action = request.form.get("action")
    if not book_ids or not action:
        flash("No books selected or invalid action.", "warning")
        return redirect(url_for("views.watchlist", state=state))
    app = current_app._get_current_object()
    print(book_ids,action)
    books = [int(book) for book in book_ids]
    def run_task():
        with app.app_context():
            return user_book_batch(user_id, books, action)

    if run_task():
        flash("Batch update successful!", "success")
        return redirect(url_for("views.books", state=state))
    else:
        flash("Action not valid")
