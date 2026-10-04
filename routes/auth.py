

"""Authentication routes for admin and students."""
import re
from flask import Blueprint, request, jsonify, session
from werkzeug.security import check_password_hash
from database.database import get_db_connection


auth_bp = Blueprint("auth", __name__, url_prefix="/api")
REGISTER_RE = re.compile(r"^\d{4,20}$")
USERNAME_RE = re.compile(r"^[A-Za-z0-9_.-]{3,30}$")


def _password_error(password):
    if not isinstance(password, str) or len(password) < 8:
        return "Password must contain at least 8 characters"
    if len(password) > 128:
        return "Password is too long"
    return None


@auth_bp.route("/admin/login", methods=["POST"])
def admin_login():
    data = request.get_json(silent=True) or {}
    username = (data.get("username") or "").strip()
    password = data.get("password") or ""
    if not USERNAME_RE.fullmatch(username):
        return jsonify({"error": "Enter a valid username"}), 400
    if _password_error(password):
        return jsonify({"error": _password_error(password)}), 400

    conn = get_db_connection()
    admin = conn.execute("SELECT * FROM admins WHERE username = ?", (username,)).fetchone()
    conn.close()
    if admin is None or not check_password_hash(admin["password"], password):
        return jsonify({"error": "Invalid username or password"}), 401

    session.clear()
    session["role"] = "admin"
    session["admin_id"] = admin["id"]
    session["username"] = admin["username"]
    return jsonify({"message": "Login successful", "role": "admin"}), 200


@auth_bp.route("/student/login", methods=["POST"])
def student_login():
    data = request.get_json(silent=True) or {}
    register_number = (data.get("register_number") or "").strip()
    password = data.get("password") or ""
    if not REGISTER_RE.fullmatch(register_number):
        return jsonify({"error": "Enter a valid register number"}), 400
    if _password_error(password):
        return jsonify({"error": _password_error(password)}), 400

    conn = get_db_connection()
    student = conn.execute("SELECT * FROM students WHERE register_number = ?", (register_number,)).fetchone()
    conn.close()
    if student is None or not check_password_hash(student["password"], password):
        return jsonify({"error": "Invalid register number or password"}), 401

    session.clear()
    session["role"] = "student"
    session["student_id"] = student["id"]
    return jsonify({"message": "Login successful", "role": "student"}), 200


@auth_bp.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({"message": "Logged out successfully"}), 200


@auth_bp.route("/session", methods=["GET"])
def session_info():
    if session.get("role") == "admin":
        return jsonify({"role": "admin", "username": session.get("username")}), 200
    if session.get("role") == "student":
        return jsonify({"role": "student", "student_id": session.get("student_id")}), 200
    return jsonify({"role": None}), 200



















