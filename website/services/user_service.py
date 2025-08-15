from werkzeug.security import generate_password_hash, check_password_hash

from book_shelf import BookShelf
from user_info import UserInfo
from website.models import User, db, UserBook,Book,Subject, UserSubject


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

def update_email(user_id,form):
    user = User.query.filter_by(id = user_id).first()
    if user and check_password_hash(user.password,form.password.data):
        user.email = form.new_email.data
        db.session.commit()
        return True
    else:
        return False


def update_password(user_id,form):
    user = User.query.filter_by(id = user_id).first()
    if user and check_password_hash(user.password,form.old_password.data):
        password = generate_password_hash(form.new_password.data)
        user.password = password
        db.session.commit()
        return True
    else:
        return False


def update_name(user_id,form):
    user = User.query.filter_by(id = user_id).first()
    if user:
        user.name = form.new_name.data
        db.session.commit()
        return True
    else:
        return False


def get_user_info(form):
    data_type = form.data_type.data
    file_name = "user_data.csv"
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
            owned_books.append(new_book_info)
    shelf.add_books(user_id, is_read=True, owned_books=owned_books)
from website.models import db, UserBook, Book, Subject, UserSubject


def delete_book(user_id, book_id):
    user_book = UserBook.query.filter_by(user_id=user_id, book_id=book_id).first()
    if not user_book:
        return False

    # Clean up subjects if no other user books use them
    for subject in user_book.book.subjects:
        still_used = (
            db.session.query(UserBook)
            .join(Book)
            .filter(
                UserBook.user_id == user_id,
                UserBook.book_id != book_id,
                Book.subjects.contains(subject)
            )
            .first()
        )
        if not still_used:
            user_subject = UserSubject.query.filter_by(
                user_id=user_id, subject_id=subject.id
            ).first()
            if user_subject:
                db.session.delete(user_subject)

    db.session.delete(user_book)
    db.session.commit()
    return True


def not_recommended(user_id, book_id):
    user_book = UserBook.query.filter_by(user_id=user_id, book_id=book_id).first()
    if not user_book:
        return False

    user_book.is_recommended = False

    for subject in user_book.book.subjects:
        user_subject = UserSubject.query.filter_by(
            user_id=user_id,
            subject_id=subject.id
        ).first()
        if user_subject:
            user_subject.is_recommended = False

    db.session.commit()
    return True


def is_read(user_id, book_id):
    user_book = UserBook.query.filter_by(user_id=user_id, book_id=book_id).first()
    if not user_book:
        return False

    user_book.is_read = True
    db.session.commit()
    return True


def user_book_batch(user_id, book_ids, action):
    action_map = {
        "delete": delete_book,
        "mark_read": is_read,
        "not_recommended": not_recommended,
    }

    handler = action_map.get(action)
    if not handler:
        return False

    for book_id in book_ids:
        handler(user_id, book_id)

    return True

def user_book_deal(user_id,book):
    user_book = db.session.execute(
        db.select(UserBook)
        .where(UserBook.user_id == user_id,
               UserBook.book_id == book['id'])
    ).scalars().first()
    user_book.deal = book['price']
    user_book.deal_link = book['link']
    db.session.commit()
