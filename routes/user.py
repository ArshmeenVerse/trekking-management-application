from flask import Blueprint
from flask import render_template
from flask import session
from flask import redirect, url_for, request, flash 
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
    total_bookings = Booking.query.join(Trek).filter(
        Booking.user_id == session.get("user_id"),
        Booking.booking_status == "Booked",
        Trek.status.in_(["Open", "Ongoing"])
    ).count()

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


@user_bp.route("/trek/<int:trek_id>")
def trek_details(trek_id):
    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    if session.get("user_role") != "trekker":
        return "Unauthorized", 403

    trek = Trek.query.get_or_404(trek_id)

    return render_template("user/trek_details.html", trek=trek)



@user_bp.route("/book-trek/<int:trek_id>")
def book_trek(trek_id): 
    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    if session.get("user_role") != "trekker":
        return "Unauthorized", 403

    trek = Trek.query.get_or_404(trek_id)

    if trek.status != "Open":
        flash("This trek is not open for booking.", "warning")
        return redirect(url_for("user.view_treks"))

    if trek.available_slots <= 0:
        flash("No available slots for this trek.", "warning")
        return redirect(url_for("user.view_treks"))

    existing_booking = Booking.query.filter_by(
        user_id=session.get("user_id"),
        trek_id=trek.id
    ).first()

    if existing_booking:
        flash("You have already booked this trek.", "warning")
        return redirect(url_for("user.view_treks"))

    booking = Booking(
        user_id=session.get("user_id"),
        trek_id=trek.id,
        booking_date=date.today(),
        booking_status="Booked"
    )
    db.session.add(booking)
    trek.available_slots -= 1
    db.session.commit()

    flash("Trek booked successfully.", "success")
    return redirect(url_for("user.view_my_bookings"))





@user_bp.route("/my-bookings")
def view_my_bookings():
    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    if session.get("user_role") != "trekker":
        return "Unauthorized", 403

    bookings = Booking.query.join(Trek).filter(
        Booking.user_id == session.get("user_id"),
        Booking.booking_status == "Booked",
        Trek.status.in_(["Open", "Ongoing"])
    ).all()

    return render_template("user/my_bookings.html", bookings=bookings)


@user_bp.route("/cancel-booking/<int:booking_id>")
def cancel_booking(booking_id):
    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    if session.get("user_role") != "trekker":
        return "Unauthorized", 403

    booking = Booking.query.get_or_404(booking_id)

    if booking.user_id != session.get("user_id"):
        return "Unauthorized", 403

    if booking.booking_status != "Booked":
        flash("Only active bookings can be cancelled.", "warning")
        return redirect(url_for("user.view_my_bookings"))

    booking.booking_status = "Cancelled"

    booking.trek.available_slots += 1
    
    db.session.commit()

    flash("Booking cancelled successfully.", "success")
    return redirect(url_for("user.view_my_bookings"))


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
        phone = request.form.get("phone")

        existing_user = User.query.filter_by(email=new_email).first()
        if existing_user and existing_user.id != user.id:
            flash("Email already exists.", "danger")
            return redirect(url_for("user.profile"))
        user.name = name
        user.email = new_email
        user.phone = phone

        db.session.commit()

        flash("Profile updated successfully.", "success")
        return redirect(url_for("user.dashboard"))

    return render_template("user/profile.html",user=user)