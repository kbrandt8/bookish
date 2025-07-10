
from werkzeug.security import generate_password_hash, check_password_hash
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
