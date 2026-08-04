from flask import Blueprint
from flask import render_template
from flask import session
from flask import redirect, url_for, request
from models import Trek, Booking, User, db

staff_bp = Blueprint("staff", __name__)

@staff_bp.route("/dashboard")
def staff_dashboard():

    # User must be logged in
    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    # User must be a staff member
    if session.get("user_role") != "staff":
        return "Unauthorized", 403

    staff_id = session.get("user_id")
    assigned_treks = Trek.query.filter_by(assigned_staff_id=staff_id).all()

    return render_template("staff/dashboard.html", assigned_treks=assigned_treks, Booking=Booking)

@staff_bp.route("/treks")
def view_assigned_treks():
    if "user_id" not in session:
        return redirect(url_for("auth.login"))      

    if session.get("user_role") != "staff":
        return "Unauthorized", 403

    staff_id = session.get("user_id")
    assigned_treks = Trek.query.filter_by(assigned_staff_id=staff_id).all()
    return render_template("staff/view_treks.html", assigned_treks=assigned_treks, Booking=Booking)


@staff_bp.route("/update-trek/<int:trek_id>", methods=["GET", "POST"])
def update_trek(trek_id):
    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    if session.get("user_role") != "staff":
        return "Unauthorized", 403

    trek = Trek.query.get_or_404(trek_id)

    
    if trek.assigned_staff_id != session.get("user_id"):
        return "Unauthorized", 403

    if request.method == "POST":
        trek.available_slots = request.form.get("available_slots")
        trek.status = request.form.get("status")
        db.session.commit()
        return redirect(url_for("staff.view_assigned_treks"))

    return render_template("staff/update_trek.html", trek=trek)


@staff_bp.route("/participants/<int:trek_id>")
def view_participants(trek_id):
    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    if session.get("user_role") != "staff":
        return "Unauthorized", 403

    trek = Trek.query.get_or_404(trek_id)

    if trek.assigned_staff_id != session.get("user_id"):
        return "Unauthorized", 403

    bookings = Booking.query.filter_by(trek_id=trek_id).all()

    return render_template("staff/view_participants.html", trek=trek, bookings=bookings)

    