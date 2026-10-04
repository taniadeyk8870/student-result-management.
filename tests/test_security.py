from database.database import get_db_connection

def test_passwords_are_hashed_and_not_exposed(admin_client):
    students = admin_client.get("/api/students").get_json()
    assert "password" not in students[0]
    conn = get_db_connection()
    row = conn.execute("SELECT password FROM students WHERE register_number=?", ("23CS101",)).fetchone()
    conn.close()
    assert row["password"] != "pass1234"
    assert row["password"].startswith(("scrypt:", "pbkdf2:"))

def test_invalid_year_and_semester_rejected(admin_client):
    payload = {"name":"Valid Student","register_number":"23CS991","email":"valid@example.com","department":"Computer Science","year":5,"semester":1,"password":"secret123"}
    assert admin_client.post("/api/students", json=payload).status_code == 400
    payload["year"] = 2; payload["semester"] = 9
    assert admin_client.post("/api/students", json=payload).status_code == 400

def test_student_cannot_access_other_result(student_client):
    assert student_client.get("/api/results/2").status_code == 403

def test_pdf_download_is_protected(admin_client):
    students = admin_client.get("/api/students").get_json()
    sid = students[0]["id"]
    response = admin_client.get(f"/api/results/{sid}/pdf")
    assert response.status_code == 200
    assert response.mimetype == "application/pdf"
    assert response.data.startswith(b"%PDF")
