# Configurations

## Purpose

In software engineering, the **configurations** folder centralizes application settings, secrets, and environment-specific parameters. This enables flexible, environment-driven deployments.

In this project, the `configurations` folder contains logic for loading and validating configuration files for the database, cache, and external APIs.

## Structure

```
configurations/
  db.py
  usda.py
  cache.py
  security.py
```

- `db.py`: Database configuration loader
- `usda.py`: USDA API configuration loader
- `cache.py`: Redis cache configuration loader
- `security.py`: Security configuration loader 