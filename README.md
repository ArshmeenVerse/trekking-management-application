# Trekking Management Application

A role-based web application built with **Flask**, **SQLite**, and **Bootstrap** to manage trekking expeditions, staff assignments, and user bookings.

Developed as part of the **Modern Application Development I (MAD-I)** course at **IIT Madras**.

---

## Features & User Roles

### 1. Admin
* **Dashboard & Metrics:** Overview of total users, active treks, bookings, and revenue/status stats.
* **Trek Management:** Create, edit, and delete treks (difficulty, duration, dates, slot capacity).
* **Staff Management:** Review and approve staff registrations, assign staff/guides to specific treks.
* **User & Booking Overview:** View registered users and monitor all expedition bookings.

### 2. Staff / Guide
* **Staff Portal:** View assigned treks and expedition schedules.
* **Participant Roster:** View list of enrolled trekkers for assigned expeditions.
* **Trek Status Updates:** Update trek progress (e.g., Pending, Ongoing, Completed).

### 3. User (Trekker)
* **Explore Treks:** Browse available treks with details (difficulty, duration, location, available slots).
* **Slot Booking:** Book spots on upcoming treks with automatic slot deduction.
* **My Bookings:** View active and past bookings with option to cancel if needed.

---

## Tech Stack

* **Backend:** Python, Flask, Flask-SQLAlchemy
* **Frontend:** Jinja2 templates, HTML5, CSS3, Bootstrap 5, Bootstrap Icons
* **Database:** SQLite
* **Authentication:** Password hashing with Werkzeug (`pbkdf2:sha256`), session-based auth

---

## Project Structure

```text
trekking-management-application/
├── app.py                  # Application entry point & DB initialization
├── models.py               # Database models (User, StaffProfile, Trek, Booking)
├── requirements.txt        # Python dependencies
├── routes/
│   ├── admin.py            # Admin routes and management views
│   ├── auth.py             # Login, register, logout handlers
│   ├── staff.py            # Staff dashboard and trek updates
│   └── user.py             # User exploration and booking routes
├── static/
│   ├── css/                # Custom stylesheets
│   ├── js/                 # Client-side scripts
│   └── images/             # Static image assets
├── templates/
│   ├── admin/              # Admin templates
│   ├── auth/               # Login & registration templates
│   ├── staff/              # Staff portal templates
│   ├── user/               # User dashboard & booking templates
│   ├── base.html           # Base layout template
│   └── home.html           # Landing page
└── instance/
    └── database.db         # SQLite database file (auto-generated)
```

---

## Getting Started

### Prerequisites
* Python 3.10+
* `pip` and `virtualenv`

### Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd trekking-management-application
   ```

2. **Create and activate a virtual environment:**
   ```bash
   # On macOS / Linux
   python3 -m venv venv
   source venv/bin/activate

   # On Windows
   python -m venv venv
   venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application:**
   ```bash
   python app.py
   ```

5. **Access the application:**
   Open your browser and navigate to `http://127.0.0.1:5001`.

---

## Default Admin Credentials

On initial startup, a default admin account is automatically seeded if it doesn't already exist:

* **Email:** `admin@example.com`
* **Password:** `admin123`
