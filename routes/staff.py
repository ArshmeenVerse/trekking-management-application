from flask import Blueprint
from flask import render_template
from flask import session
from flask import redirect, url_for

staff_bp = Blueprint("staff", __name__)

@staff_bp.route("/dashboard")

def staff_dashboard():
    return render_template("staff/dashboard.html")