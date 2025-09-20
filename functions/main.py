import os

from dotenv import load_dotenv
from flask import jsonify
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker

from book_deals import BookDeal
from book_shelf import BookShelf
from models import User, UserBook, Book, UserSubject, Subject
from user_info import UserInfo

load_dotenv()
engine = create_engine(os.getenv("SQLDB"))
Session = sessionmaker(bind=engine)
DATABASE_PATH = os.getenv("SQLDB")
engine = create_engine(DATABASE_PATH)
db = scoped_session(
    sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine,
    )
)
SQLAlchemyBase = declarative_base()
SQLAlchemyBase.query = db.query_property()

def book_functions(request):
    action = request.args.get("action", "")
    user_id = request.args.get("user_id", "")
    session = Session()
    action_map = {
        "update_recs": lambda : update_user_recs(session,user_id),
        "update_deals": lambda : update_deals(session,user_id),
        "upload_csv": lambda : upload_csv(session,user_id, request)
    }
    handler = action_map.get(action)
    if not handler:
        return jsonify({"error": "Something went Wrong"}), 400
    result = handler()
    if result:
        return result
    else:
        return jsonify({"error": "Something went Wrong"}), 400


def update_user_recs(session,user_id):
    shelf = BookShelf(session,user_id)
    if shelf.update_recs():
        print(f"User {user_id} updated!")
        return jsonify({"msg": "Updated Successfully!"})
    else:
        return jsonify({"msg": "Updated Successfully!"})



def update_deals(session,user_id):
    user_id = int(user_id)
    session = Session()
    with session.no_autoflush:
        bookshelf = (
            session.query(UserBook)
            .filter(UserBook.user_id == user_id)
            .all()
        )
    BookDeal(user_id, bookshelf, session)
    return jsonify({"msg":"Updated successfully!"})

def upload_csv(session,user_id,request):
    if "file" not in request.files:
        return jsonify({"error": "no file uploaded"}), 400
    file = request.files["file"]
    source = request.form.get("data_type", "gr")
    upload_user_info = UserInfo()
    upload_user_info.load_csv(file, source)
    books = upload_user_info.all_books

    shelf = BookShelf(session,user_id)
    owned_books = []
    for book in books:
        new_book_info = shelf.book_info(book)
        if new_book_info is not None:
            owned_books.append(new_book_info)
    book_list = shelf.check_if_read(owned_books)
    if shelf.save_books(books=book_list,is_read=True):
        return jsonify({"msg": "Books Added Successfully!"})
    else:
        return jsonify({"msg": "Error Adding Books"})
