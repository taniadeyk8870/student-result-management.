# 🎓 Student Result Management System

**With Continuous Integration**
A full-stack college project for managing student marks and results, built with
Flask, SQLite and Bootstrap. The system automatically calculates the result, and the pass/fail decision is
always made by the backend, never the browser.

## Introduction

This system lets an administrator manage students, subjects and marks, and
automatically calculates each student's total, average, grade and pass/fail
status. Students log in separately to view only their own result. The project
also ships with an automated pytest test suite and a GitHub Actions CI
pipeline that runs the tests on every push and pull request.

## Features

- Admin login and Student login with hashed passwords and session auth
- Admin dashboard with stat cards and a pass/fail chart
- Student management (add / edit / delete / search / filter)
- Subject management (add / edit / delete / search / filter)
- Marks management with validation (0–100, no duplicates)
- Backend-calculated results: total, average, grade, PASS/FAIL
- Professional result page with print/download support
- Student dashboard showing their own performance summary
- REST API for all resources with proper HTTP status codes
- Input validation and friendly error handling throughout
- Responsive, dashboard-style UI (sidebar, top bar, cards, modals)
- Automated pytest test suite
- GitHub Actions continuous integration workflow

## Technology Stack

| Layer      | Technology                                   |
|------------|-----------------------------------------------|
| Frontend   | HTML5, CSS3, JavaScript (Fetch API), Bootstrap 5, Bootstrap Icons |
| Backend    | Python 3, Flask, Flask Blueprints, Flask sessions |
| Database   | SQLite (via Python's built-in `sqlite3` module) |
| Security   | Werkzeug password hashing                    |
| Testing    | pytest, Flask test client                     |
| CI/CD      | GitHub Actions                                |

## Project Structure

```text
student-result-management/
│
├── app.py                     # Flask app factory + page routes
├── config.py                  # App configuration (secret key, DB path, rules)
├── requirements.txt
├── README.md
├── .gitignore
│
├── database/
│   └── database.py            # Connection helper, schema, demo data seeding
│
├── routes/                    # REST API blueprints
│   ├── auth.py                 # /api/admin/login, /api/student/login, /api/logout
│   ├── students.py             # /api/students CRUD
│   ├── subjects.py             # /api/subjects CRUD
│   ├── marks.py                # /api/marks CRUD
│   ├── results.py              # /api/results, /api/dashboard-stats
│   └── decorators.py           # admin_required / student_or_admin_required
│
├── services/
│   └── result_service.py      # SINGLE SOURCE OF TRUTH for result calculation
│
├── templates/                 # Jinja2 HTML templates (one per page)
├── static/
│   ├── css/                   # style.css (app-wide), result.css (result page)
│   └── js/                    # main.js, dashboard.js, results.js
│                               
│
├── tests/                     # pytest test suite
│
└── .github/workflows/ci.yml   # GitHub Actions CI pipeline
```

## Installation (Windows + VS Code)

Open the project folder in VS Code, then in the integrated terminal:

```powershell
py -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Database

The SQLite database (`database/database.db`) is created automatically the
first time the app starts. `init_db()` creates the `admins`, `students`,
`subjects`, and `marks` tables if they don't exist, and seeds:

- One demo admin account
- 5 demo subjects (CS101–CS105)
- 5 demo students
- Demo marks, including one student with a subject below the passing mark,
  so you can immediately see both the PASS and FAIL paths

Delete `database/database.db` at any time to reset to a fresh demo state.

## Running the Application

```powershell
python app.py
```

Then open:

```text
http://127.0.0.1:5000
```

## Login Credentials (Demo)

> ⚠️ These are demo credentials for local evaluation only. Change them
> before any real deployment.

| Role    | Username / Register Number | Password |
|---------|------------------------------|----------|
| Admin   | `admin`                      | `admin123` |
| Student | `23CS101` (Arun — PASS demo)  | `pass123` |
| Student | `23CS103` (Rahul — FAIL demo) | `pass123` |

## API Documentation

**Authentication**
```
POST /api/admin/login          { username, password }
POST /api/student/login        { register_number, password }
POST /api/logout
GET  /api/session               -> currently logged-in user, if any
```

**Students** (admin only)
```
GET    /api/students            ?search=&department=&year=&semester=
POST   /api/students
GET    /api/students/<id>
PUT    /api/students/<id>
DELETE /api/students/<id>
```

**Subjects** (admin only)
```
GET    /api/subjects            ?search=&department=&semester=
POST   /api/subjects
GET    /api/subjects/<id>
PUT    /api/subjects/<id>
DELETE /api/subjects/<id>
```

**Marks** (admin only)
```
GET    /api/marks               ?student_id=&subject_id=
POST   /api/marks
PUT    /api/marks/<id>
DELETE /api/marks/<id>
```

**Results**
```
GET /api/results                 (admin only – all students)
GET /api/results/<student_id>    (admin, or the student viewing their own result)
GET /api/dashboard-stats         (admin only – dashboard cards + chart data)
```

All endpoints return JSON and use standard status codes: `200`, `201`, `400`,
`401`, `404`, `500`.

## Testing

```powershell
pytest -v
```

The suite covers authentication, student CRUD, marks validation, result
calculation (total/average/grade/PASS/FAIL), and API behavior. The backend
result service is the single source of truth for the PASS/FAIL status.

## Continuous Integration

```text
Developer
    ↓
Write Code
    ↓
Git Commit
    ↓
Git Push
    ↓
GitHub
    ↓
GitHub Actions
    ↓
Install Dependencies
    ↓
Run Tests
    ↓
Syntax Check
    ↓
Application Check
    ↓
PASS / FAIL
```

The workflow at `.github/workflows/ci.yml` runs on every push and pull
request to `main`. It checks out the code, sets up Python 3.12, installs
dependencies, byte-compiles all files as a syntax check, runs the pytest
suite, and finally imports the Flask app to confirm it loads cleanly.


## Security Notes

- Passwords are hashed with Werkzeug (`generate_password_hash` /
  `check_password_hash`) — no plain-text passwords are ever stored.
- Session-based authentication with role checks (`admin_required`,
  `student_or_admin_required`) protects every write and result endpoint.
- Students can only view their own result — the backend checks
  `session["student_id"]` against the requested ID on every request.
- API responses never include the `password` field for students or admins.
- All database access uses parameterized queries (no string-built SQL),
  which prevents SQL injection.


## Security and demo setup
- Passwords are hashed with Werkzeug and are never returned by APIs.
- Demo accounts/data are opt-in. Set `SEED_DEMO_DATA=1` before the first run for a classroom demo.
- Demo admin: `admin / admin123`; demo student: `23CS101 / pass1234`. These credentials are not shown on the login page.
- `FLASK_DEBUG=0` is the default. Use `FLASK_DEBUG=1` only during development.
- The project assumes a normal 4-year course: years 1-4 and semesters 1-8. Marks are 0-100; passing mark is 35 per subject.
- `Download Result` downloads a protected PDF generated by the backend.

### Windows PowerShell demo
```powershell
$env:SEED_DEMO_DATA="1"
python app.py
```
