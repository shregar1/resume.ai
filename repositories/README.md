# Repositories

## Purpose

In software engineering, the **repository** pattern abstracts data access logic, providing a clean interface for querying and persisting data. Repositories decouple business logic from database operations.

In this project, the `repositories` folder contains classes that interact with the database for user and meal log data, using SQLAlchemy ORM.

## Structure

```
repositories/
  meal_log.py
  user.py
```

- `meal_log.py`: Repository for meal log data access
- `user.py`: Repository for user data access 