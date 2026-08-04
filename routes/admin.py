from re import search

from flask import Blueprint
from flask import render_template
from flask import session
from flask import redirect, url_for, request
from models import db,User, Trek, Booking, StaffProfile
from datetime import datetime

admin_bp = Blueprint("admin", __name__)

@admin_bp.route("/dashboard")
def dashboard():

    
    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    
    if session.get("user_role") != "admin":
        return "Unauthorized", 403

    total_users = User.query.filter_by(role="trekker").count()
    total_treks = Trek.query.count()
    total_bookings = Booking.query.count()
    total_staff = User.query.filter_by(role="staff").count()

    return render_template(
        "admin/dashboard.html", 
        total_users=total_users, 
        total_treks=total_treks, 
        total_bookings=total_bookings,
        total_staff=total_staff)

@admin_bp.route("/create_trek", methods=["GET", "POST"])
def create_trek():

    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    
    if session.get("user_role") != "admin":
        return "Unauthorized", 403

    if request.method == "POST":

        name = request.form.get("name")
        location = request.form.get("location")
        difficulty = request.form.get("difficulty")
        duration = request.form.get("duration") 
        available_slots = request.form.get("available_slots")
        start_date = datetime.strptime(request.form.get("start_date"), "%Y-%m-%d").date()
        end_date = datetime.strptime(request.form.get("end_date"), "%Y-%m-%d").date()
        
        status = request.form.get("status")

        new_trek = Trek(
            name=name,
            location=location,
            difficulty=difficulty,
            duration=duration,
            available_slots=available_slots,
            start_date=start_date,
            end_date=end_date,
            status=status
        )

        db.session.add(new_trek)
        db.session.commit()

        return redirect(url_for("admin.dashboard"))

    return render_template("admin/create_trek.html")

@admin_bp.route("/treks")  
def view_treks():

    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    
    if session.get("user_role") != "admin":
        return "Unauthorized", 403
    search = request.args.get("search","").strip()
    if search:
        if search.isdigit():
            treks = Trek.query.filter(Trek.id == int(search)).all()
        else:
            treks = Trek.query.filter(Trek.name.ilike(f"%{search}%")).all()
    else:
        treks = Trek.query.all()

    return render_template("admin/view_treks.html",treks=treks)


@admin_bp.route("/edit-trek/<int:trek_id>", methods=["GET", "POST"])
def edit_trek(trek_id):

    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    if session.get("user_role") != "admin":
        return "Unauthorized", 403

    trek = Trek.query.get_or_404(trek_id)

    if request.method == "POST":

        trek.name = request.form.get("trek_name")
        trek.location = request.form.get("location")
        trek.difficulty = request.form.get("difficulty")
        trek.duration = int(request.form.get("duration"))
        trek.available_slots = int(request.form.get("available_slots"))

        trek.start_date = datetime.strptime(
            request.form.get("start_date"),
            "%Y-%m-%d").date()

        trek.end_date = datetime.strptime(
            request.form.get("end_date"),
            "%Y-%m-%d").date()

        trek.status = request.form.get("status")

        db.session.commit()

        return redirect(url_for("admin.view_treks"))

    return render_template("admin/edit_trek.html",trek=trek)



@admin_bp.route("/delete-trek/<int:trek_id>")
def delete_trek(trek_id):

    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    if session.get("user_role") != "admin":
        return "Unauthorized", 403

    trek = Trek.query.get_or_404(trek_id)

    db.session.delete(trek)

    db.session.commit()

    return redirect(url_for("admin.view_treks"))



@admin_bp.route("/staff")
def view_staff():

    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    if  session.get("user_role") != "admin":
        return "Unauthorized", 403

    search = request.args.get("search","").strip()
    if search:
        if search.isdigit():
            staffs = StaffProfile.query.filter(StaffProfile.id == int(search)).all()
        else:
            staffs = StaffProfile.query.join(User).filter(User.name.ilike(f"%{search}%")).all()
    else:
        staffs = StaffProfile.query.all()

    return render_template(
        "admin/view_staff.html",
        staffs=staffs
    )



@admin_bp.route("/approve-staff/<int:staff_id>")
def approve_staff(staff_id):

    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    if session.get("user_role") != "admin":
        return "Unauthorized", 403

    staff = StaffProfile.query.get_or_404(staff_id)

    staff.approval_status = "approved"

    db.session.commit()

    return redirect(url_for("admin.view_staff"))



@admin_bp.route("/reject-staff/<int:staff_id>")
def reject_staff(staff_id):

    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    if session.get("user_role") != "admin":
        return "Unauthorized", 403

    staff = StaffProfile.query.get_or_404(staff_id)

    staff.approval_status = "rejected"

    db.session.commit()

    return redirect(url_for("admin.view_staff"))




@admin_bp.route("/users")
def view_users():

    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    if session.get("user_role") != "admin":
        return "Unauthorized", 403

    query = User.query.filter_by(role="trekker")
    search = request.args.get("search", "").strip()
    if search:
        if search.isdigit():
            users = query.filter(User.id == int(search)).all()
        else:
            users = query.filter(User.name.ilike(f"%{search}%")).all()
    else:
        users = query.all()
    


    return render_template(
        "admin/view_users.html",
        users=users
    )


@admin_bp.route("/block-user/<int:user_id>")
def block_user(user_id):

    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    if session.get("user_role") != "admin":
        return "Unauthorized", 403

    user = User.query.get_or_404(user_id)

    user.is_active = False

    db.session.commit()

    return redirect(url_for("admin.view_users"))



@admin_bp.route("/activate-user/<int:user_id>")
def activate_user(user_id):

    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    if session.get("user_role") != "admin":
        return "Unauthorized", 403

    user = User.query.get_or_404(user_id)

    user.is_active = True

    db.session.commit()

    return redirect(url_for("admin.view_users"))


@admin_bp.route("/assign-staff/<int:trek_id>", methods=["GET", "POST"])
def assign_staff(trek_id):

    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    if session.get("user_role") != "admin":
        return "Unauthorized", 403

    trek = Trek.query.get_or_404(trek_id)

    if request.method == "POST":

        staff_id = request.form.get("staff_id")

        staff = StaffProfile.query.get_or_404(staff_id)

        trek.assigned_staff_id = staff.user_id

        db.session.commit()

        return redirect(url_for("admin.view_treks"))

    staffs = StaffProfile.query.filter_by(approval_status="approved").all()

    return render_template(
        "admin/assign_staff.html",
        trek=trek,
        staffs=staffs
    )


@admin_bp.route("/bookings")
def view_bookings():
    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    if session.get("user_role") != "admin":
        return "Unauthorized", 403

    bookings = Booking.query.all()

    return render_template(
        "admin/view_bookings.html",
        bookings=bookings
    )
