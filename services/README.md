# Services

## Purpose

In software engineering, the **services** layer contains the core business logic of the application. Services encapsulate operations, workflows, and rules, and are called by controllers to perform actions.

In this project, the `services` folder contains all business logic for user management and API features (e.g., meal logging, recommendations). Services interact with repositories, utilities, and external APIs.

## Structure

```
services/
  __init__.py
  apis/
    abstraction.py
    v1/
      abstraction.py
      meal/
        abstraction.py
        add.py
        fetch.py
        history.py
        recommendation.py
  user/
    __init__.py
    abstraction.py
    login.py
    logout.py
    registration.py
```

- `apis/`: Business logic for API endpoints (versioned)
- `user/`: Business logic for user authentication and registration 