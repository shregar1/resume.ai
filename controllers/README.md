# Controllers

## Purpose

In software engineering, the **controllers** layer is responsible for handling incoming HTTP requests, orchestrating application logic, and returning responses. Controllers act as the interface between the client (API consumers) and the business logic/services of the application.

In this project, the `controllers` folder contains all FastAPI route handlers for user and API endpoints. Controllers validate input, invoke services, and format responses.

## Structure

```
controllers/
  apis/
    __init__.py
    v1/
      __init__.py
      meal/
        __init__.py
        add.py
        fetch.py
        history.py
        recommendation.py
  user/
    __init__.py
    login.py
    logout.py
    register.py
```

- `apis/`: API versioned controllers for business features (e.g., meal endpoints)
- `user/`: Controllers for user authentication and management 