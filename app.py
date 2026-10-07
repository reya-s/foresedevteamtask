"""
Student Records API
-------------------
A small REST API to manage student records (name, roll number,
username, department, year) with CRUD operations, validation and error handling.

Run:  python app.py
"""

import re
import sqlite3

from flask import Flask, g, jsonify, request

app = Flask(__name__)
DB_FILE = "students.db"


# ---------------------------------------------------------------
# Database helpers
# ---------------------------------------------------------------
def get_db():
    """Open one database connection per request and reuse it."""
    if "db" not in g:
        g.db = sqlite3.connect(DB_FILE)
        g.db.row_factory = sqlite3.Row  # lets us read columns by name
    return g.db


@app.teardown_appcontext
def close_db(exception):
    """Close the connection when the request ends."""
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    """Create the students table if it doesn't exist yet."""
    with sqlite3.connect(DB_FILE) as db:
        db.execute(
            """
            CREATE TABLE IF NOT EXISTS students (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                name        TEXT    NOT NULL,
                roll_number TEXT    NOT NULL UNIQUE,
                username    TEXT    NOT NULL UNIQUE,
                department  TEXT    NOT NULL,
                year        INTEGER NOT NULL
            )
            """
        )


# ---------------------------------------------------------------
# Validation
# ---------------------------------------------------------------
def validate_student(data):
    """
    Check the incoming JSON.
    Returns (clean_data, errors). If errors is not empty, reject the request.
    """
    if not isinstance(data, dict):
        return None, {"body": "Request body must be a JSON object"}

    errors = {}
    clean = {}

    # name: required, 2-100 characters, letters/space/dot/apostrophe/hyphen
    name = data.get("name")
    if not isinstance(name, str) or not name.strip():
        errors["name"] = "Name is required"
    elif not re.fullmatch(r"[A-Za-z .'-]{2,100}", name.strip()):
        errors["name"] = "Name must be 2-100 letters (spaces, . ' - allowed)"
    else:
        clean["name"] = name.strip()

    # roll_number: required, exactly 13 digits (e.g. 1234567890123)
    roll = data.get("roll_number")
    if not isinstance(roll, str) or not roll.strip():
        errors["roll_number"] = "Roll number is required and must be sent as text"
    elif not re.fullmatch(r"\d{13}", roll.strip()):
        errors["roll_number"] = "Roll number must be exactly 13 digits"
    else:
        clean["roll_number"] = roll.strip()

    # username: year (2023-2026) + 2-letter department code + 4 digits (e.g. 2025cs0001)
    username = data.get("username")
    if not isinstance(username, str) or not username.strip():
        errors["username"] = "Username is required"
    elif not re.fullmatch(r"(2023|2024|2025|2026)[A-Za-z]{2}\d{4}", username.strip()):
        errors["username"] = (
            "Username must look like 2025cs0001: year (2023-2026), "
            "2-letter department code, then 4 digits"
        )
    else:
        clean["username"] = username.strip().lower()

    # department: required, up to 100 characters
    dept = data.get("department")
    if not isinstance(dept, str) or not dept.strip():
        errors["department"] = "Department is required"
    elif len(dept.strip()) > 100:
        errors["department"] = "Department must be at most 100 characters"
    else:
        clean["department"] = dept.strip()

    # year: required, whole number from 1 to 4
    year = data.get("year")
    # bool is a kind of int in Python, so reject it explicitly
    if isinstance(year, bool) or not isinstance(year, int):
        errors["year"] = "Year must be a whole number"
    elif not 1 <= year <= 4:
        errors["year"] = "Year must be between 1 and 4"
    else:
        clean["year"] = year

    return clean, errors


def error_response(message, status, details=None):
    """Every error uses the same JSON shape."""
    body = {"error": message}
    if details:
        body["details"] = details
    return jsonify(body), status


# ---------------------------------------------------------------
# Routes (CRUD)
# ---------------------------------------------------------------
@app.route("/")
def home():
    return jsonify({"message": "Student Records API is running", "endpoint": "/students"})


# CREATE
@app.route("/students", methods=["POST"])
def create_student():
    data = request.get_json(silent=True)  # None if the JSON is broken
    if data is None:
        return error_response("Request body must be valid JSON", 400)

    clean, errors = validate_student(data)
    if errors:
        return error_response("Validation failed", 400, errors)

    db = get_db()
    try:
        cursor = db.execute(
            "INSERT INTO students (name, roll_number, username, department, year) VALUES (?, ?, ?, ?, ?)",
            (clean["name"], clean["roll_number"], clean["username"], clean["department"], clean["year"]),
        )
        db.commit()
    except sqlite3.IntegrityError:
        return error_response("Roll number or username already exists", 409)

    row = db.execute("SELECT * FROM students WHERE id = ?", (cursor.lastrowid,)).fetchone()
    return jsonify(dict(row)), 201


# READ (all, with optional ?department= filter)
@app.route("/students", methods=["GET"])
def list_students():
    department = request.args.get("department")
    db = get_db()
    if department:
        rows = db.execute(
            "SELECT * FROM students WHERE department = ? ORDER BY id", (department,)
        ).fetchall()
    else:
        rows = db.execute("SELECT * FROM students ORDER BY id").fetchall()
    return jsonify([dict(r) for r in rows]), 200


# READ (one)
@app.route("/students/<int:student_id>", methods=["GET"])
def get_student(student_id):
    row = get_db().execute("SELECT * FROM students WHERE id = ?", (student_id,)).fetchone()
    if row is None:
        return error_response("Student not found", 404)
    return jsonify(dict(row)), 200


# UPDATE
@app.route("/students/<int:student_id>", methods=["PUT"])
def update_student(student_id):
    db = get_db()
    existing = db.execute("SELECT id FROM students WHERE id = ?", (student_id,)).fetchone()
    if existing is None:
        return error_response("Student not found", 404)

    data = request.get_json(silent=True)
    if data is None:
        return error_response("Request body must be valid JSON", 400)

    clean, errors = validate_student(data)
    if errors:
        return error_response("Validation failed", 400, errors)

    try:
        db.execute(
            "UPDATE students SET name = ?, roll_number = ?, username = ?, department = ?, year = ? WHERE id = ?",
            (clean["name"], clean["roll_number"], clean["username"], clean["department"], clean["year"], student_id),
        )
        db.commit()
    except sqlite3.IntegrityError:
        return error_response("Roll number or username already exists", 409)

    row = db.execute("SELECT * FROM students WHERE id = ?", (student_id,)).fetchone()
    return jsonify(dict(row)), 200


# DELETE
@app.route("/students/<int:student_id>", methods=["DELETE"])
def delete_student(student_id):
    db = get_db()
    cursor = db.execute("DELETE FROM students WHERE id = ?", (student_id,))
    db.commit()
    if cursor.rowcount == 0:
        return error_response("Student not found", 404)
    return jsonify({"message": "Student deleted"}), 200


# ---------------------------------------------------------------
# CORS: lets a web page opened from another place (like dashboard.html
# from your folder) call this API. Browsers block it without these headers.
# ---------------------------------------------------------------
@app.after_request
def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    return response


# ---------------------------------------------------------------
# Global error handlers (so errors are always JSON, never HTML)
# ---------------------------------------------------------------
@app.errorhandler(404)
def not_found(e):
    return error_response("Route not found", 404)


@app.errorhandler(405)
def method_not_allowed(e):
    return error_response("Method not allowed for this route", 405)


@app.errorhandler(500)
def server_error(e):
    return error_response("Something went wrong on the server", 500)


init_db()

if __name__ == "__main__":
    # Port 5001, not Flask's default 5000: macOS uses 5000 for AirPlay Receiver
    app.run(debug=True, port=5001)
