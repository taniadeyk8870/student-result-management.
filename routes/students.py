"""Student management routes (admin only)."""
import re
import sqlite3
from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash
from database.database import get_db_connection
from config import Config
from routes.decorators import admin_required

students_bp = Blueprint("students", __name__, url_prefix="/api/students")
EMAIL_REGEX = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")
NAME_REGEX = re.compile(r"^[A-Za-z][A-Za-z .'-]{1,99}$")
REGISTER_REGEX = re.compile(r"^\d{4,20}$")


def _serialize(row):
    return {k: row[k] for k in ("id","name","register_number","email","department","year","semester")}


def _validate_student(data, require_password=True):
    name = (data.get("name") or "").strip()
    reg = (data.get("register_number") or "").strip()
    email = (data.get("email") or "").strip()
    department = (data.get("department") or "").strip()
    if not NAME_REGEX.fullmatch(name): return "Student name must contain valid letters and spaces"
    if not REGISTER_REGEX.fullmatch(reg): return "Register number must be 3-20 characters (letters, numbers, _ or -)"
    if not EMAIL_REGEX.fullmatch(email) or len(email) > 120: return "Enter a valid email address"
    if not department or len(department) > 100: return "Department is required"
    try: year = int(data.get("year"))
    except (TypeError, ValueError): return "Enter a valid year"
    if not Config.MIN_YEAR <= year <= Config.MAX_YEAR: return f"Year must be between {Config.MIN_YEAR} and {Config.MAX_YEAR}"
    try: semester = int(data.get("semester"))
    except (TypeError, ValueError): return "Enter a valid semester"
    if not Config.MIN_SEMESTER <= semester <= Config.MAX_SEMESTER: return f"Semester must be between {Config.MIN_SEMESTER} and {Config.MAX_SEMESTER}"
    password = data.get("password") or ""
    if require_password and len(password) < Config.MIN_PASSWORD_LENGTH: return f"Password must contain at least {Config.MIN_PASSWORD_LENGTH} characters"
    if password and len(password) > 128: return "Password is too long"
    return None


@students_bp.route("", methods=["GET"])
@admin_required
def get_students():
    query, params = "SELECT * FROM students WHERE 1=1", []
    for key in ("department","year","semester"):
        value = request.args.get(key)
        if value:
            query += f" AND {key} = ?"; params.append(value)
    search = request.args.get("search", "").strip()
    if search:
        query += " AND (name LIKE ? OR register_number LIKE ?)"; params.extend([f"%{search}%", f"%{search}%"])
    query += " ORDER BY name"
    conn = get_db_connection(); rows = conn.execute(query, params).fetchall(); conn.close()
    return jsonify([_serialize(r) for r in rows]), 200


@students_bp.route("/<int:student_id>", methods=["GET"])
@admin_required
def get_student(student_id):
    conn = get_db_connection(); row = conn.execute("SELECT * FROM students WHERE id=?", (student_id,)).fetchone(); conn.close()
    return (jsonify(_serialize(row)), 200) if row else (jsonify({"error":"Student not found"}),404)


@students_bp.route("", methods=["POST"])
@admin_required
def create_student():
    data = request.get_json(silent=True) or {}; error = _validate_student(data)
    if error: return jsonify({"error": error}), 400
    try:
        conn = get_db_connection()
        cur = conn.execute("""INSERT INTO students (name,register_number,email,department,year,semester,password) VALUES (?,?,?,?,?,?,?)""",
            ((data["name"].strip()), data["register_number"].strip(), data["email"].strip(), data["department"].strip(), int(data["year"]), int(data["semester"]), generate_password_hash(data["password"])))
        conn.commit(); new_id = cur.lastrowid; conn.close()
        return jsonify({"message":"Student created successfully","id":new_id}),201
    except sqlite3.IntegrityError:
        try: conn.close()
        except Exception: pass
        return jsonify({"error":"Register number already exists"}),400


@students_bp.route("/<int:student_id>", methods=["PUT"])
@admin_required
def update_student(student_id):
    data = request.get_json(silent=True) or {}; error = _validate_student(data, False)
    if error: return jsonify({"error":error}),400
    conn=get_db_connection(); existing=conn.execute("SELECT * FROM students WHERE id=?", (student_id,)).fetchone()
    if not existing: conn.close(); return jsonify({"error":"Student not found"}),404
    password = existing["password"]
    if (data.get("password") or ""): password=generate_password_hash(data["password"])
    try:
        conn.execute("""UPDATE students SET name=?,register_number=?,email=?,department=?,year=?,semester=?,password=? WHERE id=?""",
            (data["name"].strip(),data["register_number"].strip(),data["email"].strip(),data["department"].strip(),int(data["year"]),int(data["semester"]),password,student_id))
        conn.commit(); conn.close(); return jsonify({"message":"Student updated successfully"}),200
    except sqlite3.IntegrityError:
        conn.close(); return jsonify({"error":"Register number already exists"}),400


@students_bp.route("/<int:student_id>", methods=["DELETE"])
@admin_required
def delete_student(student_id):
    conn=get_db_connection(); existing=conn.execute("SELECT id FROM students WHERE id=?", (student_id,)).fetchone()
    if not existing: conn.close(); return jsonify({"error":"Student not found"}),404
    conn.execute("DELETE FROM students WHERE id=?", (student_id,)); conn.commit(); conn.close()
    return jsonify({"message":"Student and related marks deleted successfully"}),200
