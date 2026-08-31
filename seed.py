from backend.app import create_app
from backend.models.db import db
from backend.models.user import User
from werkzeug.security import generate_password_hash

app = create_app()

with app.app_context():
    db.create_all()
    if not User.query.first():
        admin = User(
            username='admin',
            password=generate_password_hash('admin123')
        )
        db.session.add(admin)
        db.session.commit()
        print('Default admin created: admin / admin123')
    else:
        print('Admin user already exists')
