# Student Records API

A REST API to manage student records (name, roll number, username, department, year) with CRUD operations, validation and error handling. Built with Python, Flask and SQLite. Works on Windows, macOS and Linux.

## Setup and run

You need Python 3.8 or newer. Open a terminal in the `backend` folder.

**macOS / Linux**
```
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py
```

**Windows**
```
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

The API starts at http://127.0.0.1:5001. Data is saved in `students.db`, which is created automatically. The port is 5001 (not Flask's default 5000) because macOS uses port 5000 for AirPlay Receiver.

To check everything works without starting the server: `python test_api.py`

## Try it

**Easiest:** start the API, then open `../frontend/dashboard.html` in any browser. It lists all students and lets you add, edit and delete them.

**From the terminal (macOS / Linux / Git Bash):**
```
# create
curl -X POST http://127.0.0.1:5001/students -H "Content-Type: application/json" -d '{"name":"Priya Raman","roll_number":"1234567890123","username":"2025cs0001","department":"CSE","year":2}'

# list all
curl http://127.0.0.1:5001/students

# get one
curl http://127.0.0.1:5001/students/1

# update (send all five fields)
curl -X PUT http://127.0.0.1:5001/students/1 -H "Content-Type: application/json" -d '{"name":"Priya Raman","roll_number":"1234567890123","username":"2025cs0001","department":"CSE","year":3}'

# delete
curl -X DELETE http://127.0.0.1:5001/students/1
```

**Windows PowerShell:** use `Invoke-RestMethod` instead, for example:
```
Invoke-RestMethod -Uri http://127.0.0.1:5001/students -Method Post -ContentType "application/json" -Body '{"name":"Priya Raman","roll_number":"1234567890123","username":"2025cs0001","department":"CSE","year":2}'
```

Any API tool such as Postman also works.

## Endpoints

| Method | URL | What it does | Success |
|--------|-----|--------------|---------|
| POST | /students | Create a student | 201 |
| GET | /students | List all students (optional `?department=CSE`) | 200 |
| GET | /students/<id> | Get one student | 200 |
| PUT | /students/<id> | Update a student (send all five fields) | 200 |
| DELETE | /students/<id> | Delete a student | 200 |

Example body for POST and PUT:

```json
{ "name": "Priya Raman", "roll_number": "1234567890123", "username": "2025cs0001", "department": "CSE", "year": 2 }
```

## Validation rules

- name: required, 2-100 characters, letters, spaces and . ' - only
- roll_number: required, exactly 13 digits (sent as text), must be unique
- username: required, year 2023-2026 + 2-letter department code + 4 digits, like 2025cs0001, must be unique (stored in lowercase)
- department: required, up to 100 characters
- year: required, whole number from 1 to 4

## Error responses

Every error is JSON in the same shape:

```json
{ "error": "Validation failed", "details": { "year": "Year must be between 1 and 4" } }
```

| Status | When |
|--------|------|
| 400 | Bad JSON or failed validation |
| 404 | Student or route not found |
| 405 | Wrong HTTP method for the route |
| 409 | Roll number or username already exists |
| 500 | Unexpected server error |

## Dashboard

`../frontend/dashboard.html` shows all students from this API with summary stats, search, filters, and add, edit and delete. Start the API first, then double-click the file. The API sends CORS headers so the page can call it from a local file.
