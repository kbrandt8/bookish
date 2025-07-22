from werkzeug.security import generate_password_hash, check_password_hash

from book_shelf import BookShelf
from user_info import UserInfo
from website.models import User, db


def register_new_user(form):
    name = form.name.data
    email = form.email.data.lower()
    password = generate_password_hash(form.password.data)
    if User.query.filter_by(email=email).first():
        return False
    new_user = User(email=email, name=name, password=password)
    db.session.add(new_user)
    db.session.commit()
    return True


def validate_login(email, password):
    user = User.query.filter_by(email=email.lower()).first()
    if user and check_password_hash(user.password, password):
        return user
    return None


def get_user_info(form):
    print(f"{form.data_type.data}{form.file.data}")
    data_type = form.data_type.data
    file_name = "user_data.csv"
    file = form.file.data
    file.save(file_name)
    user = UserInfo()
    user.load_csv(file_name, source=data_type)
    return user.all_books


def add_user_books(user_id, form):
    books = get_user_info(form)
    shelf = BookShelf()
    owned_books = []
    for book in books:
            new_book_info = shelf.book_info(book)
            if new_book_info is not None:
                print(new_book_info)
                owned_books.append(new_book_info)
    shelf.add_books(user_id,is_read=True, owned_books=owned_books)


