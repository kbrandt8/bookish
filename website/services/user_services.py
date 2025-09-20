from werkzeug.security import generate_password_hash, check_password_hash

from functions.models import User, db, UserSubject


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


def update_email(user_id, form):
    user = User.query.filter_by(id=user_id).first()
    if user and check_password_hash(user.password, form.password.data):
        user.email = form.new_email.data
        db.session.commit()
        return True
    else:
        return False


def update_password(user_id, form):
    user = User.query.filter_by(id=user_id).first()
    if user and check_password_hash(user.password, form.old_password.data):
        password = generate_password_hash(form.new_password.data)
        user.password = password
        db.session.commit()
        return True
    else:
        return False


def update_name(user_id, form):
    user = User.query.filter_by(id=user_id).first()
    if user:
        user.name = form.new_name.data
        db.session.commit()
        return True
    else:
        return False


def is_new_user(user_id: int) -> bool:
    return not db.session.query(
        db.exists().where(UserSubject.user_id == user_id)
    ).scalar()
