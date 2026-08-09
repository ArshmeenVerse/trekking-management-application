from flask import Flask, render_template
from models import db, User
from werkzeug.security import generate_password_hash
from routes.auth import auth_bp
from routes.admin import admin_bp
from routes.staff import staff_bp
from routes.user import user_bp

app = Flask(__name__)

app.secret_key = "my-super-secret-key"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"

db.init_app(app)

with app.app_context():
    db.create_all()

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

app.register_blueprint(auth_bp)
app.register_blueprint(admin_bp, url_prefix="/admin")
app.register_blueprint(staff_bp, url_prefix="/staff")
app.register_blueprint(user_bp, url_prefix="/user")


@app.route("/")
def home():
    return render_template("home.html")


if __name__ == "__main__":
    app.run(debug=True)