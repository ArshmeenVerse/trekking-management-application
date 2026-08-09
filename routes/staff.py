from flask import Blueprint
from flask import render_template
from flask import session
from flask import redirect, url_for, request, flash 
from models import Trek, Booking, User, db

staff_bp = Blueprint("staff", __name__)

@staff_bp.route("/dashboard")
def staff_dashboard():

    if "user_id" not in session:
        return redirect(url_for("auth.login"))


    if session.get("user_role") != "staff":
        return "Unauthorized", 403

    staff_id = session.get("user_id")
    assigned_treks = Trek.query.filter_by(assigned_staff_id=staff_id).all()

    total_assigned = len(assigned_treks)
    total_participants = Booking.query.join(Trek).filter(
        Trek.assigned_staff_id == staff_id,
        Booking.booking_status == "Booked",
        Trek.status.in_(["Open", "Ongoing"])
    ).count()
    total_open = sum(1 for trek in assigned_treks if trek.status == "Open")

    return render_template(
        "staff/dashboard.html",
        total_assigned=total_assigned,
        total_participants=total_participants,
        total_open=total_open
    )

@staff_bp.route("/treks")
def view_assigned_treks():
    if "user_id" not in session:
        return redirect(url_for("auth.login"))      

    if session.get("user_role") != "staff":
        return "Unauthorized", 403

    staff_id = session.get("user_id")
    assigned_treks = Trek.query.filter_by(assigned_staff_id=staff_id).all()
    return render_template("staff/view_treks.html", assigned_treks=assigned_treks)


@staff_bp.route("/manage-trek/<int:trek_id>", methods=["GET", "POST"])
def manage_trek(trek_id):
    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    if session.get("user_role") != "staff":
        return "Unauthorized", 403

    trek = Trek.query.get_or_404(trek_id)

    if trek.assigned_staff_id != session.get("user_id"):
        return "Unauthorized", 403

    if request.method == "POST":
        trek.available_slots = int(request.form.get("available_slots"))
        trek.status = request.form.get("status")

        db.session.commit()

        flash("Trek updated successfully.", "success")
        return redirect(url_for("staff.manage_trek", trek_id=trek.id))

    bookings = Booking.query.filter_by(trek_id=trek_id).all()

    all_statuses = ["Open", "Ongoing", "Closed", "Completed"]
    next_statuses = [s for s in all_statuses if s != trek.status]

    return render_template(
        "staff/manage_trek.html",
        trek=trek,
        bookings=bookings,
        next_statuses=next_statuses
    )

@staff_bp.route("/profile", methods=["GET", "POST"])
def profile():

    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    if session.get("user_role") != "staff":
        return "Unauthorized", 403

    user = User.query.get_or_404(session["user_id"])

    if request.method == "POST":

        name = request.form.get("name")
        new_email = request.form.get("email")
        phone = request.form.get("phone")

        existing_user = User.query.filter_by(email=new_email).first()
        if existing_user and existing_user.id != user.id:
            flash("Email already exists.", "danger")
            return redirect(url_for("staff.profile"))

        user.name = name
        user.email = new_email
        user.phone = phone

        db.session.commit()

        flash("Profile updated successfully.", "success")
        return redirect(url_for("staff.staff_dashboard"))

    return render_template("staff/profile.html", user=user)