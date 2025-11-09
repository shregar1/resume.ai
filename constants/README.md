# Constants

## Purpose

In software engineering, the **constants** folder stores static values, enums, and configuration keys used throughout the application. This improves maintainability and avoids magic strings.

In this project, the `constants` folder contains API status codes, payload types, default values, regular expressions, and meal-related constants.

## Structure

```
constants/
  api_lk.py
  api_status.py
  db/
    table.py
  default.py
  meal/
    category.py
    nutrients.py
    prompt/
      instructions.py
      recommendation.py
  payload_type.py
  regular_expression.py
```

- `api_lk.py`: API lookup keys
- `api_status.py`: API status codes
- `db/`: Database table constants
- `default.py`: Default values
- `meal/`: Meal-related constants and prompts
- `payload_type.py`: Payload type enums
- `regular_expression.py`: Regular expressions for validation 