from flask import Blueprint, render_template, request, redirect, url_for, session
from models import User,StaffProfile, db

auth_bp = Blueprint('auth', __name__)

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        user = User.query.filter_by(email=email).first()

        if user is None:
            return "Invalid email or password."

        if user.password != password:
            return "Invalid email or password."

        if not user.is_active:
            return "Your account is blocked by the admin."
        
        if user.role == "staff" and user.staff_profile.approval_status != "approved":
            return "Waiting for admin approval."


        if user.role == "staff":
            session["user_id"] = user.id
            session["user_role"] = user.role
            return redirect(url_for("staff.dashboard"))
        
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
    return redirect(url_for("auth.login"))



@auth_bp.route("/register")
def register():
    return render_template("auth/register.html")

@auth_bp.route("/register/user", methods=["GET", "POST"])
def register_user():
    if request.method == "POST":
         
        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")
        role = "trekker"

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return "User with this email already exists."

        new_user = User(name=name, email=email, password=password, role="trekker")  
        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for("auth.login"))
    return render_template("auth/register_user.html")
   

@auth_bp.route("/register/staff", methods=["GET", "POST"])
def register_staff():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")
        contact_number = request.form.get("contact_number")
        

        existing_staff = User.query.filter_by(email=email).first()
        if existing_staff:
            return "Staff with this email already exists."

        new_staff = User(name=name, email=email, password=password, role="staff")
        db.session.add(new_staff)
        db.session.commit()

        staff_profile = StaffProfile(user_id=new_staff.id, contact_number=contact_number, approval_status="Pending" )
        db.session.add(staff_profile)
        db.session.commit()

        return redirect(url_for("auth.login"))
    return render_template("auth/register_staff.html")

