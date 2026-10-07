# FORESE Tech Tasks

Two small projects for the FORESE tech team recruitment.

1. **Student Records API (backend)**: a REST API with full CRUD, validation and error handling. Built with Python, Flask and SQLite. It lives in `backend/`.
2. **Student Profile Card (frontend)**: a responsive profile card with login, create, edit and delete, plus an optional dashboard that lists all students from the API. It lives in `frontend/`.

## 1. Student Records API

Each student has a name, roll number, username, department and year.

Open a terminal in the `backend` folder (needs Python 3.8 or newer).

macOS / Linux:
```
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py
```

Windows:
```
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

The API runs at http://127.0.0.1:5001. To check everything works, run `python test_api.py` (27 checks).

| Method | URL | Action |
|--------|-----|--------|
| POST | /students | Create a student |
| GET | /students | List all students |
| GET | /students/<id> | Get one student |
| PUT | /students/<id> | Update a student |
| DELETE | /students/<id> | Delete a student |

Validation: name is 2 to 100 letters; roll number is exactly 13 digits; username is a year from 2023 to 2026, a 2-letter department code and 4 digits; year is 1 to 4. Roll numbers and usernames must be unique. Errors come back as JSON with the right status code (400, 404, 405, 409, 500). See `backend/README.md` for curl examples.

## 2. Student Profile Card

No install needed. Open `frontend/index.html` in any browser.

- Log in with your username to see only your own profile, or create a new profile.
- Edit your details (photo, department, year, skills, social links) or delete your profile.
- Works on phones and laptops.
- Profiles are saved in the browser's local storage.

Dashboard (optional): start the API first, then open `frontend/dashboard.html`. It shows all students from the API with stats, search, filters, and add, edit and delete.

## Tech

Python, Flask, SQLite, HTML, CSS, JavaScript.
