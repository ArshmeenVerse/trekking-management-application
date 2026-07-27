from flask import Blueprint
from flask import render_template
from flask import session
from flask import redirect, url_for

admin_bp = Blueprint("admin", __name__)

@admin_bp.route("/dashboard")
def admin_dashboard():
    if "user_id" not in session:
        return redirect(url_for("auth.login"))
    return render_template("admin/dashboard.html")
