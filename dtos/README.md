# Data Transfer Objects (DTOs)

## Purpose

In software engineering, **DTOs** are used to transfer data between layers of an application in a type-safe and structured way. DTOs help validate, serialize, and document the data exchanged between APIs, services, and databases.

In this project, the `dtos` folder contains all request and response schemas, as well as configuration and service-specific DTOs, using Pydantic for validation.

## Structure

```
dtos/
  configurations/
    cache.py
    db.py
    security.py
    usda.py
  requests/
    abstraction.py
    apis/
      v1/
        meal/
          add.py
          fetch.py
          history.py
          recommendation.py
    user/
      login.py
      logout.py
      registration.py
  responses/
    base.py
  service/
    api/
      meal/
        instructions.py
        recommendation.py
```

- `configurations/`: DTOs for configuration files
- `requests/`: DTOs for API request payloads
- `responses/`: DTOs for API responses
- `service/`: DTOs for internal service logic 