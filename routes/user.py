from flask import Blueprint
from flask import render_template
from flask import session
from flask import redirect, url_for, request
from datetime import date, datetime

from models import User
from models import Trek
from models import Booking
from models import db

user_bp = Blueprint("user", __name__)

@user_bp.route("/dashboard")
def dashboard():

    
    if "user_id" not in session:
        return redirect(url_for("auth.login"))

   
    if session.get("user_role") != "trekker":
        return "Unauthorized", 403

    total_open = Trek.query.filter(Trek.status == "Open").count()
    total_bookings = Booking.query.filter_by(user_id=session.get("user_id")).count()

    return render_template("user/dashboard.html", total_open=total_open, total_bookings=total_bookings)


@user_bp.route("/treks")
def view_treks():
    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    if session.get("user_role") != "trekker":
        return "Unauthorized", 403

    search = request.args.get("search", "").strip()
    difficulty = request.args.get("difficulty", "").strip()
    location = request.args.get("location", "").strip()
    query = Trek.query.filter(Trek.status == "Open")

    if search:
        query = query.filter(Trek.name.ilike(f"%{search}%"))
    if difficulty:
        query = query.filter(Trek.difficulty == difficulty)
    if location:
        query = query.filter(Trek.location.ilike(f"%{location}%"))

    treks = query.all()
    return render_template("user/view_treks.html", treks=treks, search=search, difficulty=difficulty, location=location)


@user_bp.route("/book-trek/<int:trek_id>")
def book_trek(trek_id):
    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    if session.get("user_role") != "trekker":
        return "Unauthorized", 403

    trek = Trek.query.get_or_404(trek_id)

    if trek.status != "Open":
        return "This trek is not open for booking."

    if trek.available_slots <= 0:
        return "No available slots for this trek."

    existing_booking = Booking.query.filter_by(user_id=session.get("user_id"), trek_id=trek.id).first()

    if existing_booking:
        return "You have already booked this trek."

    booking = Booking(
        user_id=session.get("user_id"),
        trek_id=trek.id,
        booking_date=date.today(),
        booking_status="Confirmed"
    )
    db.session.add(booking)
    trek.available_slots -= 1
    db.session.commit()

    return redirect(url_for("user.view_my_bookings"))




@user_bp.route("/my-bookings")
def view_my_bookings():
    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    if session.get("user_role") != "trekker":
        return "Unauthorized", 403

    bookings = Booking.query.filter_by(user_id=session.get("user_id")).all()
    return render_template("user/view_my_bookings.html", bookings=bookings)


@user_bp.route("/history")
def history():
   
    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    if session.get("user_role") != "trekker":
        return "Unauthorized", 403

    bookings = Booking.query.filter_by(
        user_id=session["user_id"]).all()

    return render_template("user/history.html",bookings=bookings)


@user_bp.route("/profile", methods=["GET", "POST"])
def profile():

    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    if session.get("user_role") != "trekker":
        return "Unauthorized", 403

    user = User.query.get_or_404(session["user_id"])

    if request.method == "POST":

        name = request.form.get("name")
        new_email = request.form.get("email")

        existing_user = User.query.filter_by(email=new_email).first()
        if existing_user and existing_user.id != user.id:
            return "Email already exists."

        user.name = name
        user.email = new_email

        db.session.commit()

        return redirect(url_for("user.dashboard"))

    return render_template("user/profile.html",user=user)