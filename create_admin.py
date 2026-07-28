from models import db,User 

def create_admin():
    admin = User.query.filter_by(role="admin").first()
    if admin is None:
        admin = User(name="admin", email="admin@example.com", password="admin123", role="admin", is_active=True)
        db.session.add(admin)
        db.session.commit()
