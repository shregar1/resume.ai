# Middlewares

## Purpose

In software engineering, **middleware** components process requests and responses globally, adding cross-cutting concerns like authentication, rate limiting, and security headers.

In this project, the `middlewares` folder contains FastAPI middleware for authentication, rate limiting, security, and request context management.

## Structure

```
middlewares/
  authetication.py
  rate_limit.py
  request_context.py
  security_headers.py
```

- `authetication.py`: Middleware for user authentication
- `rate_limit.py`: Middleware for API rate limiting
- `request_context.py`: Middleware for request context propagation
- `security_headers.py`: Middleware for security headers 