"""Result APIs and secure PDF download."""
from io import BytesIO
from flask import Blueprint, jsonify, session, send_file
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from services.result_service import calculate_result, calculate_all_results, get_dashboard_stats
from routes.decorators import admin_required, student_or_admin_required

results_bp=Blueprint("results",__name__,url_prefix="/api")

@results_bp.route("/results",methods=["GET"])
@admin_required
def get_all_results(): return jsonify(calculate_all_results()),200

@results_bp.route("/results/<int:student_id>",methods=["GET"])
@student_or_admin_required
def get_student_result(student_id):
    if session.get("role")=="student" and session.get("student_id")!=student_id:
        return jsonify({"error":"Unauthorized access to this result"}),403
    result=calculate_result(student_id)
    if result is None:return jsonify({"error":"Student not found"}),404
    return jsonify(result),200

@results_bp.route("/results/<int:student_id>/pdf",methods=["GET"])
@student_or_admin_required
def download_result_pdf(student_id):
    if session.get("role")=="student" and session.get("student_id")!=student_id:
        return jsonify({"error":"Unauthorized access to this result"}),403
    result=calculate_result(student_id)
    if result is None:return jsonify({"error":"Student not found"}),404
    if result["status"]=="NO_RESULT":return jsonify({"error":"No marks are available for this student"}),404

    buffer=BytesIO()
    doc=SimpleDocTemplate(buffer,pagesize=A4,rightMargin=18*mm,leftMargin=18*mm,topMargin=18*mm,bottomMargin=18*mm)
    styles=getSampleStyleSheet(); story=[]
    story.append(Paragraph("Student Result Management System",styles["Title"]))
    story.append(Spacer(1,8))
    info=[["Student Name",result["name"]],["Register / ID",result["register_number"]],["Department",result["department"]],["Year",str(result["year"])],["Semester",str(result["semester"])]]
    t=Table(info,colWidths=[45*mm,125*mm]);t.setStyle(TableStyle([("BACKGROUND",(0,0),(0,-1),colors.whitesmoke),("GRID",(0,0),(-1,-1),0.5,colors.grey),("VALIGN",(0,0),(-1,-1),"TOP"),("FONTNAME",(0,0),(0,-1),"Helvetica-Bold")]))
    story += [t,Spacer(1,12)]
    rows=[["Subject Code","Subject","Marks"]]+[[s["subject_code"],s["subject_name"],str(s["marks"])] for s in result["subjects"]]
    st=Table(rows,colWidths=[35*mm,105*mm,30*mm]);st.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),colors.HexColor("#4361ee")),("TEXTCOLOR",(0,0),(-1,0),colors.white),("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),("GRID",(0,0),(-1,-1),0.5,colors.grey),("ALIGN",(2,1),(2,-1),"CENTER")]))
    story += [st,Spacer(1,12)]
    summary=[["Total",str(result["total"])],["Average",str(result["average"])],["Grade",result["grade"]],["Status",result["status"]]]
    sm=Table(summary,colWidths=[45*mm,55*mm]);sm.setStyle(TableStyle([("GRID",(0,0),(-1,-1),0.5,colors.grey),("FONTNAME",(0,0),(0,-1),"Helvetica-Bold")]))
    story.append(sm);doc.build(story);buffer.seek(0)
    safe_reg="".join(c if c.isalnum() or c in "-_" else "_" for c in result["register_number"])
    return send_file(buffer,as_attachment=True,download_name=f"result_{safe_reg}.pdf",mimetype="application/pdf")

@results_bp.route("/dashboard-stats",methods=["GET"])
@admin_required
def dashboard_stats(): return jsonify(get_dashboard_stats()),200
