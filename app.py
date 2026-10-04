"""
Student Result Management System
Main Flask application entry point.
"""

from flask import Flask, render_template, session, redirect, url_for

from config import Config
from database.database import init_db, get_db_connection

from routes.auth import auth_bp
from routes.students import students_bp
from routes.subjects import subjects_bp
from routes.marks import marks_bp
from routes.results import results_bp


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # =========================================================
    # Register API blueprints
    # =========================================================

    app.register_blueprint(auth_bp)
    app.register_blueprint(students_bp)
    app.register_blueprint(subjects_bp)
    app.register_blueprint(marks_bp)
    app.register_blueprint(results_bp)

    # =========================================================
    # Page Routes
    # =========================================================

    # ---------------------------------------------------------
    # Home → Login
    # ---------------------------------------------------------

    @app.route("/")
    def index():
        return redirect(url_for("login_page"))

    # ---------------------------------------------------------
    # About Page
    # ---------------------------------------------------------

    @app.route("/about")
    def about():
        return render_template("about.html")

    # ---------------------------------------------------------
    # Login Page
    # ---------------------------------------------------------

    @app.route("/login")
    def login_page():
        return render_template("login.html")

    # =========================================================
    # Admin Pages
    # =========================================================

    @app.route("/admin/dashboard")
    def admin_dashboard():

        if session.get("role") != "admin":
            return redirect(url_for("login_page"))

        return render_template(
            "admin_dashboard.html",
            username=session.get("username")
        )

    # ---------------------------------------------------------
    # Students
    # ---------------------------------------------------------

    @app.route("/admin/students")
    def students_page():

        if session.get("role") != "admin":
            return redirect(url_for("login_page"))

        return render_template("students.html")

    # ---------------------------------------------------------
    # Subjects
    # ---------------------------------------------------------

    @app.route("/admin/subjects")
    def subjects_page():

        if session.get("role") != "admin":
            return redirect(url_for("login_page"))

        return render_template("subjects.html")

    # ---------------------------------------------------------
    # Marks
    # ---------------------------------------------------------

    @app.route("/admin/marks")
    def marks_page():

        if session.get("role") != "admin":
            return redirect(url_for("login_page"))

        return render_template("marks.html")

    # ---------------------------------------------------------
    # Results
    # ---------------------------------------------------------

    @app.route("/admin/results")
    def results_page():

        if session.get("role") != "admin":
            return redirect(url_for("login_page"))

        return render_template("results.html")

    # ---------------------------------------------------------
    # Admin View Student Result
    # ---------------------------------------------------------

    @app.route("/admin/result/<int:student_id>")
    def admin_view_result(student_id):

        if session.get("role") != "admin":
            return redirect(url_for("login_page"))

        return render_template(
            "result.html",
            student_id=student_id,
            viewer="admin"
        )

    # =========================================================
    # Student Pages
    # =========================================================

    @app.route("/student/dashboard")
    def student_dashboard():

        # Make sure the user is logged in as a student
        if session.get("role") != "student":
            return redirect(url_for("login_page"))

        # Get the logged-in student's ID
        student_id = session.get("student_id")

        # If no student ID exists in the session,
        # send the user back to login
        if not student_id:
            session.clear()
            return redirect(url_for("login_page"))

        # Get the student's actual name from the database
        conn = get_db_connection()

        student = conn.execute(
            """
            SELECT name
            FROM students
            WHERE id = ?
            """,
            (student_id,)
        ).fetchone()

        conn.close()

        # If the student exists, use their database name
        if student:
            student_name = student["name"]
        else:
            student_name = "Student"

        # Send the name to student_dashboard.html
        return render_template(
            "student_dashboard.html",
            name=student_name
        )

    # ---------------------------------------------------------
    # Student Result
    # ---------------------------------------------------------

    @app.route("/student/result")
    def student_result():

        if session.get("role") != "student":
            return redirect(url_for("login_page"))

        student_id = session.get("student_id")

        if not student_id:
            session.clear()
            return redirect(url_for("login_page"))

        return render_template(
            "result.html",
            student_id=student_id,
            viewer="student"
        )

    # =========================================================
    # Error Handlers
    # =========================================================

    @app.errorhandler(404)
    def not_found(error):
        return redirect(url_for("login_page"))

    @app.errorhandler(400)
    def bad_request(error):
        return {
            "error": "Invalid request"
        }, 400

    @app.errorhandler(500)
    def server_error(error):
        return {
            "error": "Internal server error"
        }, 500

    return app


# =============================================================
# Create Application
# =============================================================

app = create_app()


# =============================================================
# Run Application
# =============================================================

if __name__ == "__main__":

    # Initialize database
    init_db()

    # Start Flask server
    app.run(
        debug=app.config["DEBUG"]
    )

