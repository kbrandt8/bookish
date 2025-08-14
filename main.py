from website import create_app, db
from flask import current_app

app = create_app()

# Optional: create tables automatically on import
with app.app_context():
    db.create_all()
