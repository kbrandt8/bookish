from functions.models import User,UserBook,db,Book,UserSubject


def delete_book(user_id, book_id):
    user_book = UserBook.query.filter_by(user_id=user_id, book_id=book_id).first()
    if not user_book:
        return False

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


def user_book_deal(user_id, book):
    user_book = db.session.execute(
        db.select(UserBook)
        .where(UserBook.user_id == user_id,
               UserBook.book_id == book['id'])
    ).scalars().first()
    user_book.deal = book['price']
    user_book.deal_link = book['link']
    db.session.commit()