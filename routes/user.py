from flask import Blueprint
from flask import render_template
from flask import session
from flask import redirect, url_for

user_bp = Blueprint("user", __name__)

@user_bp.route("/dashboard")
def dashboard():

    # User must be logged in
    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    # User must be a trekker
    if session.get("user_role") != "trekker":
        return "Unauthorized", 403

    return render_template("user/dashboard.html")