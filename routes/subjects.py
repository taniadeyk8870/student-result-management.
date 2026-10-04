"""Subject management routes (admin only)."""
import re, sqlite3
from flask import Blueprint, request, jsonify
from database.database import get_db_connection
from config import Config
from routes.decorators import admin_required
subjects_bp=Blueprint("subjects",__name__,url_prefix="/api/subjects")
CODE_RE=re.compile(r"^[A-Za-z0-9_-]{2,20}$")
DEPARTMENTS = {
    "AI&DS",
    "CSE",
    "IT",
    "EEE",
    "ECE",
    "MECH",
}

def _serialize(row): return {k:row[k] for k in ("id","subject_code","subject_name","department","semester")}
def _validate_subject(data):
    code=(data.get("subject_code") or "").strip(); name=(data.get("subject_name") or "").strip(); dept=(data.get("department") or "").strip()
    if not CODE_RE.fullmatch(code): return "Subject code must be 2-20 letters/numbers"
    if not name or len(name)>100: return "Subject name is required"
    if not dept or len(dept)>100: return "Department is required"
    try: sem=int(data.get("semester"))
    except (TypeError,ValueError): return "Enter a valid semester"
    if not Config.MIN_SEMESTER<=sem<=Config.MAX_SEMESTER: return f"Semester must be between {Config.MIN_SEMESTER} and {Config.MAX_SEMESTER}"
    return None
@subjects_bp.route("",methods=["GET"])
@admin_required
def get_subjects():
    q="SELECT * FROM subjects WHERE 1=1"; p=[]
    for key in ("department","semester"):
        v=request.args.get(key)
        if v:q+=f" AND {key}=?";p.append(v)
    search=request.args.get("search","").strip()
    if search:q+=" AND (subject_name LIKE ? OR subject_code LIKE ?)";p += [f"%{search}%",f"%{search}%"]
    q+=" ORDER BY subject_code";conn=get_db_connection();rows=conn.execute(q,p).fetchall();conn.close();return jsonify([_serialize(r) for r in rows]),200
@subjects_bp.route("/<int:subject_id>",methods=["GET"])
@admin_required
def get_subject(subject_id):
    conn=get_db_connection();r=conn.execute("SELECT * FROM subjects WHERE id=?",(subject_id,)).fetchone();conn.close();return (jsonify(_serialize(r)),200) if r else (jsonify({"error":"Subject not found"}),404)
@subjects_bp.route("",methods=["POST"])
@admin_required
def create_subject():
    d=request.get_json(silent=True) or {};e=_validate_subject(d)
    if e:return jsonify({"error":e}),400
    try:
        conn=get_db_connection();cur=conn.execute("INSERT INTO subjects(subject_code,subject_name,department,semester) VALUES(?,?,?,?)",(d["subject_code"].strip(),d["subject_name"].strip(),d["department"].strip(),int(d["semester"])));conn.commit();i=cur.lastrowid;conn.close();return jsonify({"message":"Subject created successfully","id":i}),201
    except sqlite3.IntegrityError:
        try:conn.close()
        except:pass
        return jsonify({"error":"Subject code already exists"}),400
@subjects_bp.route("/<int:subject_id>",methods=["PUT"])
@admin_required
def update_subject(subject_id):
    d=request.get_json(silent=True) or {};e=_validate_subject(d)
    if e:return jsonify({"error":e}),400
    conn=get_db_connection()
    if not conn.execute("SELECT id FROM subjects WHERE id=?",(subject_id,)).fetchone():conn.close();return jsonify({"error":"Subject not found"}),404
    try:conn.execute("UPDATE subjects SET subject_code=?,subject_name=?,department=?,semester=? WHERE id=?",(d["subject_code"].strip(),d["subject_name"].strip(),d["department"].strip(),int(d["semester"]),subject_id));conn.commit();conn.close();return jsonify({"message":"Subject updated successfully"}),200
    except sqlite3.IntegrityError:conn.close();return jsonify({"error":"Subject code already exists"}),400
@subjects_bp.route("/<int:subject_id>",methods=["DELETE"])
@admin_required
def delete_subject(subject_id):
    conn=get_db_connection();r=conn.execute("SELECT id FROM subjects WHERE id=?",(subject_id,)).fetchone()
    if not r:conn.close();return jsonify({"error":"Subject not found"}),404
    conn.execute("DELETE FROM subjects WHERE id=?",(subject_id,));conn.commit();conn.close();return jsonify({"message":"Subject and related marks deleted successfully"}),200
