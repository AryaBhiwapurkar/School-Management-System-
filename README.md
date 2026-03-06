# School Management System API

A production-style RESTful backend for managing school entities such as classes, sections, students, and teachers.

This project was built to practice real backend engineering concepts including database design, API architecture, authentication, logging, and structured error handling.

---

## Tech Stack

* Python
* Django
* Django REST Framework
* PostgreSQL
* JWT Authentication (SimpleJWT)
* Gunicorn (WSGI server)
* WhiteNoise (static file handling)
* Django Filters
* Custom Exception Handling
* Structured Logging

---

## Project Features

### Core Features

* Class management
* Section management
* Student management
* Teacher assignment to sections
* Nested API resources
* Filtering support
* Pagination

### Backend Engineering Features

* JWT Authentication
* Role-based permission control
* Custom global exception handler
* Structured error responses
* Application logging
* Database constraints for data integrity
* Optimized ORM queries using `select_related`

---

## Database Schema

Relationships:

```
Class
 └── Sections
        └── Students

Section
 └── Class Teacher
```

### Class

* id
* grade
* academic_year

Constraint:

```
UNIQUE (grade, academic_year)
```

---

### Section

* id
* class_section
* school_class (FK → Class)
* class_teacher (FK → Teacher)

Constraint:

```
UNIQUE (school_class, class_section)
```

---

### Student

* id
* name
* roll_number
* section (FK → Section)

Constraint:

```
UNIQUE (section, roll_number)
```

---

### Teacher

* id
* name
* employee_id (unique)

---

## API Endpoints

### Classes

```
GET    /classes/
POST   /classes/
GET    /classes/{id}/
DELETE /classes/{id}/
```

---

### Sections

```
GET    /classes/{class_id}/sections
POST   /classes/{class_id}/sections
GET    /sections/{id}/
DELETE /sections/{id}/
```

---

### Students

```
GET    /students/
GET    /students/{id}/
PUT    /students/{id}/
DELETE /students/{id}/

GET    /sections/{section_id}/students/
POST   /sections/{section_id}/students/
```

---

### Teacher Assignment

```
GET    /sections/{section_id}/teacher/
PUT    /sections/{section_id}/teacher/
DELETE /sections/{section_id}/teacher/
```

---

## Authentication

JWT authentication is used.

Obtain token:

```
POST /api/token/
```

Refresh token:

```
POST /api/token/refresh/
```

---

## Example Error Response

All errors follow a structured format:

```json
{
  "error": {
    "type": "validation_error",
    "code": "invalid_input",
    "message": "Validation failed",
    "fields": {
      "roll_number": [
        "Roll number must be between 1 and 100"
      ]
    }
  }
}
```

---

## Logging

Application logs are written to:

```
app.log
```

Events logged include:

* student creation
* student update
* student deletion
* section creation
* class creation
* teacher assignment

---

## Running the Project Locally

### 1. Clone repository

```
git clone https://github.com/AryaBhiwapurkar/School-Management-System-.git
cd school-management-system
```

---

### 2. Create virtual environment

```
python -m venv venv
source venv/bin/activate
```

---

### 3. Install dependencies

```
pip install -r requirements.txt
```

---

### 4. Configure environment variables

Create `.env` file:

```
SECRET_KEY=
DEBUG=True

DB_NAME=
DB_USER=
DB_PASSWORD=
DB_HOST=
DB_PORT=
```

---

### 5. Run migrations

```
python manage.py migrate
```

---

### 6. Start server

```
python manage.py runserver
```

---

## Learning Goals of This Project

This project focuses on understanding:

* REST API design
* relational database modeling
* Django ORM optimization
* exception handling
* logging strategies
* authentication systems
* backend architecture

---

## Future Improvements

* API test suite
* Docker containerization
* Production deployment
* CI/CD pipeline
