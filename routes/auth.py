from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from models import User, StaffProfile, db
from werkzeug.security import generate_password_hash, check_password_hash

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        user = User.query.filter_by(email=email).first()

        if user is None:
            flash("Invalid email or password.", "danger")
            return redirect(url_for("auth.login"))

        if not check_password_hash(user.password, password):
            flash("Invalid email or password.", "danger")
            return redirect(url_for("auth.login"))

        if not user.is_active:
            flash("Your account has been blocked by the admin.", "danger")
            return redirect(url_for("auth.login"))

        if user.role == "staff" and user.staff_profile.approval_status != "Approved":
            flash("Your staff account is waiting for admin approval.", "warning")
            return redirect(url_for("auth.login"))

        if user.role == "staff":
            session["user_id"] = user.id
            session["user_role"] = user.role
            return redirect(url_for("staff.staff_dashboard"))

        elif user.role == "admin":
            session["user_id"] = user.id
            session["user_role"] = user.role
            return redirect(url_for("admin.dashboard"))

        elif user.role == "trekker":
            session["user_id"] = user.id
            session["user_role"] = user.role
            return redirect(url_for("user.dashboard"))

    return render_template("auth/login.html")


@auth_bp.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out successfully.", "success")
    return redirect(url_for("auth.login"))


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":

        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")
        phone = request.form.get("phone")
        role = request.form.get("role")

        if password != confirm_password:
            flash("Password and Confirm Password do not match.", "danger")
            return redirect(url_for("auth.register"))
        
        if role not in ("trekker", "staff"):
            flash("Please select a valid role.", "warning")
            return redirect(url_for("auth.register"))

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash("An account with this email already exists.", "danger")
            return redirect(url_for("auth.register"))

        new_user = User(
            name=name,
            email=email,
            password=generate_password_hash(password, method="pbkdf2:sha256"),
            phone=phone,
            role=role,
        )

        db.session.add(new_user)
        db.session.commit()

        if role == "staff":
            staff_profile = StaffProfile(
                user_id=new_user.id,
                approval_status="Pending"
            )
            db.session.add(staff_profile)
            db.session.commit()

        flash("Registration successful. Please log in.", "success")
        return redirect(url_for("auth.login"))

    return render_template("auth/register.html")