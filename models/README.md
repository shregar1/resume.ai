# Models

## Purpose

In software engineering, the **models** layer defines the structure of data entities, typically mapping to database tables. Models are used by ORMs to interact with the database in an object-oriented way.

In this project, the `models` folder contains SQLAlchemy ORM models for users and meal logs.

## Structure

```
models/
  __init__.py
  meal_log.py
  user.py
```

- `meal_log.py`: Model for meal log entries
- `user.py`: Model for user accounts 