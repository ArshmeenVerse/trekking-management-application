from models import db, User
from werkzeug.security import generate_password_hash


def create_admin():
    admin = User.query.filter_by(role="admin").first()

    if admin is None:
        admin = User(
            name="admin",
            email="admin@example.com",
            phone="1234567890",
            password=generate_password_hash("admin123", method="pbkdf2:sha256"),
            role="admin",
            is_active=True
        )

        db.session.add(admin)
        db.session.commit()