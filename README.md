# 🏫 school-management-api

![Django](https://img.shields.io/badge/Django-4.x-092E20?style=for-the-badge&logo=django&logoColor=white)
![DRF](https://img.shields.io/badge/Django_REST_Framework-3.x-red?style=for-the-badge)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-316192?style=for-the-badge&logo=postgresql&logoColor=white)
![JWT](https://img.shields.io/badge/JWT-Auth-black?style=for-the-badge&logo=jsonwebtokens)
![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)

A RESTful backend API for managing school data — classes, sections, teachers, and students. Built with Django REST Framework, JWT authentication, and PostgreSQL.

Designed with a clean layered architecture: models handle the schema, serializers handle validation and transformation, views handle request logic, and a custom exception handler ensures every error response follows the same JSON structure.

---

## 📑 Table of Contents

- [Features](#features)
- [Architecture](#architecture)
- [Project Structure](#project-structure)
- [Design Decisions](#design-decisions)
- [Getting Started](#getting-started)
- [API Overview](#api-overview)
- [Sample Requests & Responses](#sample-requests--responses)
- [Error Handling](#error-handling)
- [Future Improvements](#future-improvements)

---

## ✨ Features

- JWT-based authentication with access/refresh token flow
- Role-based access: read-only for all, write access for staff/admin only
- Full CRUD for Classes, Sections, Students
- Teacher assignment to sections with uniqueness enforcement (one teacher per section)
- Query-param filtering on student list (`?name=`, `?section=`, `?school_class=`)
- Automatic pagination on all list endpoints
- Consistent error response format across all endpoints
- Structured logging for both business events and exceptions
- Django admin panel for direct data management

---

## 🏗 Architecture

```
┌─────────────────────────────────────────────────────────┐
│                        Client                           │
│              (Postman / Frontend / Script)              │
└────────────────────────┬────────────────────────────────┘
                         │ HTTP Request
                         ▼
┌─────────────────────────────────────────────────────────┐
│                      urls.py                            │
│           Route matched → View dispatched               │
└────────────────────────┬────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│              Authentication + Permissions               │
│   JWTAuthentication → sets request.user                 │
│   IsAdminOrReadOnly → allows or rejects                 │
└────────────────────────┬────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│                      views.py                           │
│   Generic CBVs (ListCreateAPIView, etc.) + APIView      │
│   get_queryset() → filter → paginate                    │
│   perform_create/update/destroy() → logging hooks       │
└──────────┬──────────────────────────┬───────────────────┘
           │                          │
           ▼                          ▼
┌─────────────────┐        ┌──────────────────────┐
│  serializers.py │        │      filters.py       │
│  Validate input │        │  ?name= ?section= etc │
│  Write to DB    │        └──────────────────────┘
│  Serialize out  │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────────────────────────────┐
│                      models.py                          │
│         Django ORM → PostgreSQL                         │
│   Class → Section → Student                             │
│              ↑                                          │
│           Teacher (optional FK on Section)              │
└─────────────────────────────────────────────────────────┘
         │
         ▼  (any exception at any layer)
┌─────────────────────────────────────────────────────────┐
│                   exceptions.py                         │
│   Catches all errors → returns unified JSON shape       │
└─────────────────────────────────────────────────────────┘
```

### Data Model

```
Class
 └── Section (many per class)
      ├── Teacher (optional, one per section)
      └── Student (many per section)
```

- Deleting a **Class** cascades to its Sections, then to their Students
- Deleting a **Section** cascades to its Students
- Deleting a **Teacher** sets the section's teacher field to `null` — section is preserved

---

## 📁 Project Structure

```
school-management-api/
├── school/                  # Django project root
│   ├── settings.py          # All configuration
│   ├── urls.py              # Root URL config
│   └── wsgi.py
├── core/                    # Main application
│   ├── models.py            # DB schema: Class, Teacher, Section, Student
│   ├── serializers.py       # Read/write serializers, validation
│   ├── views.py             # All API endpoint logic
│   ├── urls.py              # API URL routing
│   ├── permissions.py       # IsAdminOrReadOnly
│   ├── exceptions.py        # Custom exception handler
│   ├── filters.py           # StudentFilter
│   ├── logging_util.py      # Business event logging
│   └── admin.py             # Admin panel registration
├── .env.example             # Environment variable template
├── manage.py
└── requirements.txt
```

---

## 🧠 Design Decisions

### 1. Separate Read and Write Serializers
Write serializers (`StudentSerializer`, `SectionSerializer`) accept flat input and inject FK values from the URL. Read serializers (`StudentReadSerializer`, `ClassReadSerializer`) return nested JSON with full related objects. Mixing both in one serializer creates awkward tradeoffs — this separation keeps each clean and purposeful.

### 2. Custom Exception Handler
DRF returns inconsistently shaped errors by default — some have `detail`, some have field names, crashes return HTML. Every consumer of this API would need to handle multiple error shapes. The custom handler in `exceptions.py` normalises every error — validation, 404, permission denied, or crashes — into one JSON structure, making frontend integration predictable.

### 3. JWT over Session Authentication
Session-based auth ties state to the server, which complicates horizontal scaling. JWT tokens are stateless — the server just verifies the signature. This makes the API ready to scale without shared session storage. Sessions are kept as a fallback for the Django admin panel only.

### 4. URL-Scoped Resource Creation
Students are created via `POST /sections/<id>/students/` rather than `POST /students/` with a section ID in the body. This makes the relationship explicit in the URL, prevents clients from assigning students to arbitrary sections, and follows REST resource nesting conventions.

### 5. DB-Level Constraints + Application-Level Error Translation
Unique constraints (roll number per section, section label per class, grade+year per class) live in the DB via `UniqueConstraint`. The application catches `IntegrityError` and translates it into a clean `ValidationError` with a human-readable message — so the defense is at the DB level, but the error experience is at the API level.

### 6. IsAdminOrReadOnly Permission Design
Public read access lets any consumer (dashboards, parent portals, reporting tools) fetch data without authentication. Write access is locked to `is_staff=True` users. This is enforced per-view, overriding the global `IsAuthenticated` default in settings.

---

## 🚀 Getting Started

### Prerequisites

- Python 3.11+
- PostgreSQL running locally (or update `DB_HOST` to point to a remote instance)

### 1. Clone the repo

```bash
git clone https://github.com/your-username/school-management-api.git
cd school-management-api
```

### 2. Create and activate a virtual environment

```bash
python -m venv venv
source venv/bin/activate        # Linux/Mac
venv\Scripts\activate           # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set up environment variables

```bash
cp .env.example .env
```

Edit `.env` with your values:

```env
SECRET_KEY=your-secret-key-here
DEBUG=True

DB_NAME=school_db
DB_USER=postgres
DB_PASSWORD=yourpassword
DB_HOST=localhost
DB_PORT=5432
```

### 5. Create the database and run migrations

```bash
createdb school_db       # or create via pgAdmin
python manage.py migrate
```

### 6. Create a superuser (for admin + write access)

```bash
python manage.py createsuperuser
```

### 7. Run the development server

```bash
python manage.py runserver
```

API is now available at `http://localhost:8000/`
Admin panel at `http://localhost:8000/admin`

---

## 🗺 API Overview

All endpoints are prefixed with the base URL. Authentication uses `Authorization: Bearer <token>`.

| Method | Endpoint | Auth Required | Description |
|--------|----------|---------------|-------------|
| POST | `/api/token/` | No | Login — get access + refresh tokens |
| POST | `/api/token/refresh/` | No | Get new access token using refresh token |
| GET | `/classes/` | No | List all classes |
| POST | `/classes/` | Admin | Create a class |
| GET | `/classes/<id>/` | No | Get class with all its sections |
| DELETE | `/classes/<id>/` | Admin | Delete class (cascades to sections + students) |
| GET | `/classes/<id>/sections/` | No | List sections in a class |
| POST | `/classes/<id>/sections/` | Admin | Create a section in a class |
| GET | `/sections/<id>/` | No | Get a section |
| DELETE | `/sections/<id>/` | Admin | Delete section (cascades to students) |
| GET | `/sections/<id>/students/` | No | List students in a section |
| POST | `/sections/<id>/students/` | Admin | Add a student to a section |
| GET | `/students/` | No | List all students (filterable) |
| GET | `/students/<id>/` | No | Get a single student |
| PUT/PATCH | `/students/<id>/` | Admin | Update student |
| DELETE | `/students/<id>/` | Admin | Delete student |
| GET | `/sections/<id>/teacher/` | No | Get assigned teacher |
| PUT | `/sections/<id>/teacher/` | Admin | Assign teacher to section |
| DELETE | `/sections/<id>/teacher/` | Admin | Unassign teacher from section |

---

## 📬 Sample Requests & Responses

### Authentication

**POST** `/api/token/`

Request:
```json
{
  "username": "admin",
  "password": "yourpassword"
}
```

Response `200 OK`:
```json
{
  "access": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

Use the `access` token in all subsequent requests:
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

---

### Create a Class

**POST** `/classes/`

Request:
```json
{
  "grade": 10,
  "academic_year": 2025
}
```

Response `201 Created`:
```json
{
  "id": 1,
  "grade": 10,
  "academic_year": 2025
}
```

---

### Get a Class with Sections

**GET** `/classes/1/`

Response `200 OK`:
```json
{
  "id": 1,
  "grade": 10,
  "academic_year": 2025,
  "sections": [
    {
      "id": 1,
      "class_section": "A",
      "school_class": {
        "id": 1,
        "grade": 10,
        "academic_year": 2025
      }
    },
    {
      "id": 2,
      "class_section": "B",
      "school_class": {
        "id": 1,
        "grade": 10,
        "academic_year": 2025
      }
    }
  ]
}
```

---

### List Students with Filters

**GET** `/students/?school_class=1&name=ali`

Response `200 OK`:
```json
{
  "count": 2,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 3,
      "name": "Ali Khan",
      "roll_number": 4,
      "section": {
        "id": 1,
        "class_section": "A",
        "school_class": {
          "id": 1,
          "grade": 10,
          "academic_year": 2025
        }
      }
    },
    {
      "id": 7,
      "name": "Aaliya Sharma",
      "roll_number": 11,
      "section": {
        "id": 2,
        "class_section": "B",
        "school_class": {
          "id": 1,
          "grade": 10,
          "academic_year": 2025
        }
      }
    }
  ]
}
```

---

### Assign a Teacher to a Section

**PUT** `/sections/1/teacher/`

Request:
```json
{
  "teacher_id": 3
}
```

Response `200 OK`:
```json
{
  "teacher": {
    "id": 3,
    "name": "Priya Nair",
    "employee_id": "EMP003"
  }
}
```

---

## ⚠️ Error Handling

All errors — validation failures, not found, permission denied, or server crashes — return the same JSON structure:

```json
{
  "error": {
    "type": "...",
    "code": "...",
    "message": "...",
    "fields": {}
  }
}
```

### Validation Error `400`

```json
{
  "error": {
    "type": "validation_error",
    "code": "invalid_input",
    "message": "Validation failed",
    "fields": {
      "roll_number": ["Roll number must be between 1 and 100"]
    }
  }
}
```

### Not Found `404`

```json
{
  "error": {
    "type": "not_found",
    "code": "resource_not_found",
    "message": "Student not found",
    "fields": {}
  }
}
```

### Permission Denied `403`

```json
{
  "error": {
    "type": "permission_denied",
    "code": "not_allowed",
    "message": "You do not have permission to perform this action.",
    "fields": {}
  }
}
```

### Teacher Already Assigned `400`

```json
{
  "error": {
    "type": "validation_error",
    "code": "invalid_input",
    "message": "Validation failed",
    "fields": {
      "teacher_id": ["This teacher is already assigned to another section."]
    }
  }
}
```

---

## 🔮 Future Improvements

- **Student Marks / Results module** — store subject-wise marks per student per term, with grade computation
- **Teacher model expansion** — add subject specialisation, contact info, joining date
- **Role-based permissions** — granular roles (class teacher can edit own section only, principal has full access)
- **Bulk student import** — CSV upload endpoint to onboard an entire class at once
- **Attendance tracking** — daily attendance per student with reporting endpoints
- **Token blacklisting** — invalidate JWT tokens on logout for better security
- **API versioning** — `/api/v1/` prefix to support non-breaking evolution
- **Rate limiting** — prevent abuse on public read endpoints
- **Containerisation** — Dockerfile + docker-compose for consistent local and production setup

---

## 📄 License

MIT
