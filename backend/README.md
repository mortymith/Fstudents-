# FastAPI REST API Project

A modern, scalable REST API built with FastAPI following best practices and clean architecture principles.

## 🚀 Project Structure

```
├── app/
│   ├── main.py                 # FastAPI application entry point
│   ├── core/                   # Core configuration and settings
│   ├── routes/                 # API route handlers
│   ├── models/                 # Database models 
│   ├── repositories/           # Data access layer
│   ├── schemas/                # Pydantic schemas for request/response
│   ├── services/               # Business logic and service layer
│   ├── utils/                  # Utility functions and helpers
│   └── dependencies/           # FastAPI dependencies and DI
├── tests/                      # Test suite
├── Dockerfile                  # Docker image configuration
├── docker-compose.yml          # Multi-container setup
├── .env                        # Environment variables
└── requirements.txt            # Python dependencies
```

## 📁 Directory Overview

### `/app` - Application Source Code

- **`main.py`** - FastAPI application initialization, middleware setup, and route inclusion
- **`routes/`** - API endpoint definitions and route handlers
  - Organizes endpoints by domain/feature
  - Handles HTTP requests and responses
  - Minimal business logic (delegates to services)

- **`core/`** - Core application configuration
  - Settings management (environment variables)
  - Database configuration
  - Security setup (JWT, OAuth2)
  - Application constants

- **`models/`** - Database models
  - SQLAlchemy ORM models
  - Database table definitions
  - Relationships and constraints

- **`schemas/`** - Pydantic schemas
  - Request/response models
  - Data validation
  - Serialization/deserialization
  - Separate from database models

- **`services/`** - Business logic layer
  - Core application logic
  - Data processing and transformations
  - External API integrations
  - Database operations (via models)

- **`utils/`** - Utility functions
  - Helper functions
  - Common utilities
  - Custom exceptions
  - Logging configuration

- **`dependencies/`** - FastAPI dependencies
  - Dependency injection setup
  - Authentication dependencies
  - Database session management
  - Custom dependency providers

### `/tests` - Test Suite

- Unit tests, integration tests, and API tests
- Test fixtures and utilities
- Organized to mirror the application structure

### Configuration Files

- **`Dockerfile`** - Containerization configuration
- **`docker-compose.yml`** - Multi-service Docker setup (API, database, etc.)
- **`.env`** - Environment variables (database URLs, secrets, etc.)
- **`requirements.txt`** - Python package dependencies


### Local Development

1. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

### Docker Development

1. **Build and run with Docker Compose**
   ```bash
   docker compose up --build
   ```

2. **Access the application**
   - API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs
   - Alternative Docs: http://localhost:8000/redoc

## 🏗️ Architecture Principles

- **Separation of Concerns**: Clear separation between routes, business logic, and data access
- **Dependency Injection**: Clean dependency management using FastAPI's DI system
- **Type Safety**: Comprehensive type hints and Pydantic validation
- **Testing**: Easy-to-test components with clear boundaries
- **Scalability**: Modular structure supporting feature-based development

## 📚 API Documentation

Once the application is running, access the automatic interactive API documentation:

- **Swagger UI**: `/docs`
- **ReDoc**: `/redoc`

## 🧪 Testing

Run the test suite:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app

# Run specific test module
pytest tests/<test_module>.py
```
