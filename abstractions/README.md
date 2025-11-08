# Abstractions

## Purpose

In software engineering, the **abstractions** folder contains base classes and interfaces that define contracts for controllers, services, repositories, utilities, and errors. This promotes loose coupling and testability.

In this project, the `abstractions` folder provides interfaces and base classes for all major layers, ensuring consistent architecture and easier mocking/testing.

## Structure

```
abstractions/
  controller.py
  dependency.py
  error.py
  factory.py
  repository.py
  service.py
  utility.py
```

- `controller.py`: Base controller interface
- `dependency.py`: Dependency injection abstractions
- `error.py`: Error interface
- `factory.py`: Factory pattern abstractions
- `repository.py`: Repository interface
- `service.py`: Service interface
- `utility.py`: Utility interface 