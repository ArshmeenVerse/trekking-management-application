from flask import Flask
from models import db 
from create_admin import create_admin
from routes.auth import auth_bp
from routes.admin import admin_bp
from routes.staff import staff_bp

app = Flask(__name__)   
app.secret_key = "my-super-secret-key"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db" 

db.init_app(app)

with app.app_context():
    db.create_all()
    create_admin()


app.register_blueprint(auth_bp)
app.register_blueprint(admin_bp, url_prefix="/admin")
app.register_blueprint(staff_bp, url_prefix="/staff")

if __name__ == "__main__":
    app.run(debug=True)
        