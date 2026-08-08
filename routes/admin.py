from flask import Blueprint
from flask import render_template
from flask import session
from flask import redirect, url_for, request, flash
from models import db, User, Trek, Booking, StaffProfile
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
    total_bookings = Booking.query.join(Trek).filter(
        Booking.booking_status == "Booked",
        Trek.status.in_(["Open", "Ongoing"])
    ).count()
    total_staff = User.query.filter_by(role="staff").count()

    return render_template(
        "admin/dashboard.html", 
        total_users=total_users, 
        total_treks=total_treks, 
        total_bookings=total_bookings,
        total_staff=total_staff)

@admin_bp.route("/create-trek", methods=["GET", "POST"])
def create_trek():

    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    if session.get("user_role") != "admin":
        return "Unauthorized", 403

    if request.method == "POST":

        name = request.form.get("name")
        location = request.form.get("location")
        difficulty = request.form.get("difficulty")
        duration = int(request.form.get("duration"))
        available_slots = int(request.form.get("available_slots"))
        description = request.form.get("description")

        start_date = datetime.strptime(
            request.form.get("start_date"),
            "%Y-%m-%d"
        ).date()

        end_date = datetime.strptime(
            request.form.get("end_date"),
            "%Y-%m-%d"
        ).date()

        status = request.form.get("status")
        assigned_staff_id = request.form.get("assigned_staff_id")

        new_trek = Trek(
            name=name,
            location=location,
            difficulty=difficulty,
            duration=duration,
            available_slots=available_slots,
            description=description,
            start_date=start_date,
            end_date=end_date,
            status=status
        )

        if assigned_staff_id:
            new_trek.assigned_staff_id = int(assigned_staff_id)

        db.session.add(new_trek)
        db.session.commit()

        flash("Trek created successfully.", "success")
        return redirect(url_for("admin.create_trek"))

    staffs = User.query.join(StaffProfile).filter(
        StaffProfile.approval_status == "Approved"
    ).all()

    search = request.args.get("search", "").strip()
    trek_query = Trek.query

    if search:
        if search.isdigit():
            trek_query = trek_query.filter(Trek.id == int(search))
        else:
            trek_query = trek_query.filter(Trek.name.ilike(f"%{search}%"))

    treks = trek_query.all()

    return render_template(
        "admin/trek_form.html",
        trek=None,
        staffs=staffs,
        treks=treks,
        search=search
    )

@admin_bp.route("/edit-trek/<int:trek_id>", methods=["GET", "POST"])
def edit_trek(trek_id):

    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    if session.get("user_role") != "admin":
        return "Unauthorized", 403

    trek = Trek.query.get_or_404(trek_id)

    if request.method == "POST":

        trek.name = request.form.get("name")
        trek.location = request.form.get("location")
        trek.difficulty = request.form.get("difficulty")
        trek.duration = int(request.form.get("duration"))
        trek.available_slots = int(request.form.get("available_slots"))
        trek.description = request.form.get("description")

        trek.start_date = datetime.strptime(
            request.form.get("start_date"),
            "%Y-%m-%d"
        ).date()

        trek.end_date = datetime.strptime(
            request.form.get("end_date"),
            "%Y-%m-%d"
        ).date()

        # The status dropdown in trek_form.html only ever offers the
        # current status plus the next valid one (Pending -> Approved),
        # so we can just take it as-is.
        trek.status = request.form.get("status")

        # The Assign Staff field only renders in the template once the
        # trek is Approved or Open, so this is only ever submitted then.
        assigned_staff_id = request.form.get("assigned_staff_id")

        if assigned_staff_id:
            trek.assigned_staff_id = int(assigned_staff_id)
        else:
            trek.assigned_staff_id = None

        db.session.commit()

        flash("Trek updated successfully.", "success")
        return redirect(url_for("admin.create_trek"))

    staffs = User.query.join(StaffProfile).filter(
        StaffProfile.approval_status == "Approved"
    ).all()

    search = request.args.get("search", "").strip()
    trek_query = Trek.query

    if search:
        if search.isdigit():
            trek_query = trek_query.filter(Trek.id == int(search))
        else:
            trek_query = trek_query.filter(Trek.name.ilike(f"%{search}%"))

    treks = trek_query.all()

    return render_template(
        "admin/trek_form.html",
        trek=trek,
        staffs=staffs,
        treks=treks,
        search=search
    )

@admin_bp.route("/delete-trek/<int:trek_id>")
def delete_trek(trek_id):

    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    if session.get("user_role") != "admin":
        return "Unauthorized", 403

    trek = Trek.query.get_or_404(trek_id)

    for booking in trek.bookings:
        db.session.delete(booking)

    db.session.delete(trek)
    db.session.commit()

    flash("Trek deleted successfully.", "success")
    return redirect(url_for("admin.create_trek"))


@admin_bp.route("/staff")
def view_staff():

    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    if  session.get("user_role") != "admin":
        return "Unauthorized", 403

    status_filter = request.args.get("status", "Pending")
    search = request.args.get("search","").strip()

    query = StaffProfile.query.filter_by(approval_status=status_filter)

    if search:
        if search.isdigit():
            query = query.filter(StaffProfile.id == int(search))
        else:
            query = query.join(User).filter(User.name.ilike(f"%{search}%"))

    staffs = query.all()

    pending_count = StaffProfile.query.filter_by(approval_status="Pending").count()
    approved_count = StaffProfile.query.filter_by(approval_status="Approved").count()
    blacklisted_count = StaffProfile.query.filter_by(approval_status="Blacklisted").count()

    return render_template(
        "admin/view_staff.html",
        staffs=staffs,
        status_filter=status_filter,
        search=search,
        pending_count=pending_count,
        approved_count=approved_count,
        blacklisted_count=blacklisted_count
    )



@admin_bp.route("/approve-staff/<int:staff_id>")
def approve_staff(staff_id):

    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    if session.get("user_role") != "admin":
        return "Unauthorized", 403

    staff = StaffProfile.query.get_or_404(staff_id)

    staff.approval_status = "Approved"

    db.session.commit()

    flash("Staff approved successfully.", "success")
    return redirect(url_for("admin.view_staff"))



@admin_bp.route("/blacklist-staff/<int:staff_id>")
def blacklist_staff(staff_id):

    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    if session.get("user_role") != "admin":
        return "Unauthorized", 403

    staff = StaffProfile.query.get_or_404(staff_id)

    staff.approval_status = "Blacklisted"

    db.session.commit()

    flash("Staff has been blacklisted.", "warning")
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

    flash("User blocked successfully.", "warning")
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

    flash("User activated successfully.", "success")
    return redirect(url_for("admin.view_users"))


@admin_bp.route("/bookings")
def view_bookings():
    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    if session.get("user_role") != "admin":
        return "Unauthorized", 403

    bookings = Booking.query.join(Trek).filter(
        Booking.booking_status == "Booked",
        Trek.status.in_(["Open", "Ongoing"])
    ).all()

    return render_template(
        "admin/view_bookings.html",
        bookings=bookings
    )


@admin_bp.route("/history")
def history():

    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    if session.get("user_role") != "admin":
        return "Unauthorized", 403

    status_filter = request.args.get("status", "All")

    query = Booking.query

    if status_filter != "All":
        query = query.filter(Booking.booking_status == status_filter)

    bookings = query.order_by(Booking.booking_date.desc()).all()

    completed_count = Booking.query.filter_by(booking_status="Completed").count()
    cancelled_count = Booking.query.filter_by(booking_status="Cancelled").count()

    return render_template(
        "admin/history.html",
        bookings=bookings,
        status_filter=status_filter,
        completed_count=completed_count,
        cancelled_count=cancelled_count
    )