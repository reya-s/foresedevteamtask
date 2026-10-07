"""
Quick self-test for the Student Records API.
Uses a temporary database, so your real students.db is untouched.

Run:  python test_api.py
"""

import os
import tempfile

import app as api

api.DB_FILE = os.path.join(tempfile.mkdtemp(), "test.db")
api.init_db()
client = api.app.test_client()

passed = 0
failed = 0


def check(label, response, expected_status):
    global passed, failed
    ok = response.status_code == expected_status
    passed += ok
    failed += not ok
    print(f"[{'PASS' if ok else 'FAIL'}] {label} -> {response.status_code}")


good = {
    "name": "Priya Raman",
    "roll_number": "1234567890123",
    "username": "2025cs0001",
    "department": "CSE",
    "year": 2,
}
other = {"roll_number": "1234567890124", "username": "2024ad0101"}  # a second, different student

check("Create student", client.post("/students", json=good), 201)
check("Duplicate roll number is rejected", client.post("/students", json={**good, "username": other["username"]}), 409)
check("Duplicate username is rejected", client.post("/students", json={**good, "roll_number": other["roll_number"]}), 409)
check("Second student with a different dept code", client.post("/students", json={**good, **other}), 201)
check("Roll number with 12 digits is rejected", client.post("/students", json={**good, "roll_number": "123456789012"}), 400)
check("Roll number with letters is rejected", client.post("/students", json={**good, "roll_number": "12345678abcde"}), 400)
check("Roll number sent as a number is rejected", client.post("/students", json={**good, "roll_number": 1234567890125}), 400)
check("Username year 2022 is rejected", client.post("/students", json={**good, "username": "2022cs0001"}), 400)
check("Username year 2027 is rejected", client.post("/students", json={**good, "username": "2027cs0001"}), 400)
check("Username with 3-letter dept is rejected", client.post("/students", json={**good, "username": "2025cse0001"}), 400)
check("Username with 3 digits is rejected", client.post("/students", json={**good, "username": "2025cs000"}), 400)
check("Empty name is rejected", client.post("/students", json={**good, "name": ""}), 400)
check("Year 9 is rejected", client.post("/students", json={**good, "year": 9}), 400)
check("Year as text is rejected", client.post("/students", json={**good, "year": "two"}), 400)
check("Broken JSON is rejected", client.post("/students", data="not json", content_type="application/json"), 400)
check("List students", client.get("/students"), 200)
check("Get one student", client.get("/students/1"), 200)
check("Get missing student", client.get("/students/99"), 404)
check("Update student", client.put("/students/1", json={**good, "year": 3}), 200)
check("Update to another student's username is rejected", client.put("/students/1", json={**good, "username": other["username"]}), 409)
check("Update missing student", client.put("/students/99", json=good), 404)
check("Delete student", client.delete("/students/1"), 200)
check("Delete again (already gone)", client.delete("/students/1"), 404)
check("Unknown route", client.get("/nothing"), 404)
check("Wrong method", client.patch("/students"), 405)

preflight = client.options("/students", headers={"Origin": "null", "Access-Control-Request-Method": "POST"})
check("Browser preflight (OPTIONS) is allowed", preflight, 200)
cors_ok = preflight.headers.get("Access-Control-Allow-Origin") == "*"
passed += cors_ok
failed += not cors_ok
print(f"[{'PASS' if cors_ok else 'FAIL'}] CORS header is sent")

print(f"\n{passed} passed, {failed} failed")
