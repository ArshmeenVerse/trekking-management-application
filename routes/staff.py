from flask import Blueprint
from flask import render_template
from flask import session
from flask import redirect, url_for

staff_bp = Blueprint("staff", __name__)

@staff_bp.route("/dashboard")
def staff_dashboard():

    # User must be logged in
    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    # User must be a staff member
    if session.get("user_role") != "staff":
        return "Unauthorized", 403

    return render_template("staff/dashboard.html")