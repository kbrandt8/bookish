import os
from website import create_app, db

app = create_app()

if __name__ == '__main__':
    with app.app_context():
        if os.getenv("FLASK_ENV") == "development":
            db.create_all()
    app.run(debug=True, threaded=True)