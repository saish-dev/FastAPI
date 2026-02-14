# FastAPI Production Template

A production-ready FastAPI template with clean architecture, async SQLAlchemy 2.0, JWT authentication, and comprehensive DevOps setup.

## 🚀 Features

- **FastAPI** - Modern, fast web framework for building APIs
- **Python 3.12** - Latest Python with type hints
- **Async SQLAlchemy 2.0** - Async ORM with PostgreSQL
- **Pydantic v2** - Data validation using Python type annotations
- **JWT Authentication** - Secure access and refresh token system
- **Clean Architecture** - Feature-based modular structure
- **Repository Pattern** - Separation of data access logic
- **Service Layer** - Business logic isolation
- **Dependency Injection** - Proper DI throughout the application
- **Alembic** - Database migrations
- **Redis** - Caching and rate limiting
- **Celery** - Background task processing
- **Docker** - Containerization with docker-compose
- **Pytest** - Async testing with coverage
- **Pre-commit** - Code quality hooks
- **GitHub Actions** - CI/CD pipeline
- **Structured Logging** - JSON and colored console logging
- **Exception Handling** - Centralized error handling
- **Rate Limiting** - API rate limiting middleware
- **CORS** - Configurable CORS middleware
- **OpenAPI** - Auto-generated API documentation

## 📁 Project Structure

```
app/
├── main.py                 # FastAPI application entry point
├── dependencies.py         # Global dependencies
├── celery_app.py          # Celery configuration
│
├── core/                   # Core functionality
│   ├── config.py          # Settings and configuration
│   ├── security.py        # JWT and password hashing
│   ├── logging.py         # Structured logging
│   └── exceptions.py      # Custom exceptions
│
├── db/                     # Database configuration
│   ├── base.py            # SQLAlchemy base and models
│   └── session.py         # Async session management
│
├── api/                    # API versioning
│   └── v1/
│       └── router.py      # API v1 router aggregation
│
├── users/                  # Users feature module
│   ├── models.py          # User database model
│   ├── schemas.py         # Pydantic schemas
│   ├── repository.py      # Data access layer
│   ├── service.py         # Business logic
│   ├── router.py          # API endpoints
│   └── dependencies.py    # Feature dependencies
│
├── auth/                   # Authentication module
│   ├── schemas.py         # Auth schemas
│   ├── service.py         # Auth business logic
│   ├── router.py          # Auth endpoints
│   └── dependencies.py    # Auth dependencies
│
└── tasks/                  # Background tasks
    └── example.py         # Example Celery tasks

tests/                      # Test suite
├── conftest.py            # Pytest fixtures
└── test_api.py            # API tests

alembic/                    # Database migrations
├── versions/              # Migration files
└── env.py                 # Alembic configuration
```

## 🛠️ Setup

### Prerequisites

- Python 3.12+
- Docker and Docker Compose
- PostgreSQL (if running locally)
- Redis (if running locally)

### Installation

1. **Clone the repository**

```bash
git clone <repository-url>
cd fastapi-production-template
```

2. **Create virtual environment**

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**

```bash
make install
# or
pip install -r requirements.txt
```

4. **Install development dependencies**

```bash
make dev-install
```

5. **Set up environment variables**

```bash
cp .env.example .env
# Edit .env with your configuration
```

6. **Start services with Docker**

```bash
make docker-up
# or
docker-compose up -d
```

7. **Run database migrations**

```bash
make migrate
# or
alembic upgrade head
```

8. **Run the application**

```bash
make run
# or
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

- **API Documentation**: http://localhost:8000/api/v1/docs
- **ReDoc**: http://localhost:8000/api/v1/redoc
- **Health Check**: http://localhost:8000/health

## 🐳 Docker Usage

### Start all services

```bash
docker-compose up -d
```

Services:
- **app**: FastAPI application (port 8000)
- **db**: PostgreSQL database (port 5432)
- **redis**: Redis cache (port 6379)
- **celery_worker**: Celery worker
- **celery_beat**: Celery scheduler

### View logs

```bash
make docker-logs
# or
docker-compose logs -f
```

### Stop services

```bash
make docker-down
# or
docker-compose down
```

## 📝 Database Migrations

### Create a new migration

```bash
make migration
# or
alembic revision --autogenerate -m "description"
```

### Apply migrations

```bash
make migrate
# or
alembic upgrade head
```

### Rollback migration

```bash
make downgrade
# or
alembic downgrade -1
```

## 🧪 Testing

### Run all tests

```bash
make test
# or
pytest -v --cov=app
```

### Run specific test file

```bash
pytest tests/test_api.py -v
```

### Generate coverage report

```bash
pytest --cov=app --cov-report=html
```

## 🎨 Code Quality

### Format code

```bash
make format
# or
black app tests
ruff check --fix app tests
```

### Run linters

```bash
make lint
# or
ruff check app tests
mypy app
```

### Pre-commit hooks

```bash
pre-commit install
pre-commit run --all-files
```

## 🔐 Authentication

### Register a user

```bash
curl -X POST "http://localhost:8000/api/v1/users/" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securepassword123",
    "full_name": "John Doe"
  }'
```

### Login

```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securepassword123"
  }'
```

### Get current user

```bash
curl -X GET "http://localhost:8000/api/v1/auth/me" \
  -H "Authorization: Bearer <access_token>"
```

### Refresh token

```bash
curl -X POST "http://localhost:8000/api/v1/auth/refresh" \
  -H "Content-Type: application/json" \
  -d '{
    "refresh_token": "<refresh_token>"
  }'
```

## 📊 Background Tasks

### Example Celery task

```python
from app.tasks.example import send_email_task

# Trigger task
result = send_email_task.delay(
    email="user@example.com",
    subject="Welcome",
    body="Welcome to our platform!"
)

# Check task status
print(result.status)
```

## 🔧 Configuration

All configuration is managed through environment variables. See `.env.example` for available options.

Key configurations:
- `DATABASE_URL`: PostgreSQL connection string
- `REDIS_URL`: Redis connection string
- `SECRET_KEY`: JWT secret key (change in production!)
- `ENVIRONMENT`: development/production
- `LOG_LEVEL`: Logging level
- `RATE_LIMIT_PER_MINUTE`: API rate limit

## 🏗️ Architecture Principles

### Clean Architecture

- **Separation of Concerns**: Each layer has a specific responsibility
- **Dependency Inversion**: High-level modules don't depend on low-level modules
- **Testability**: Easy to test each layer independently

### Layers

1. **API Layer** (`router.py`): HTTP request/response handling
2. **Service Layer** (`service.py`): Business logic
3. **Repository Layer** (`repository.py`): Data access
4. **Model Layer** (`models.py`): Database models

### Dependency Injection

All dependencies are injected through FastAPI's dependency injection system, making the code:
- More testable
- More maintainable
- Easier to mock

## 📚 API Endpoints

### Health

- `GET /health` - Health check

### Authentication

- `POST /api/v1/auth/login` - Login
- `POST /api/v1/auth/refresh` - Refresh token
- `GET /api/v1/auth/me` - Get current user

### Users

- `GET /api/v1/users/` - List users
- `POST /api/v1/users/` - Create user
- `GET /api/v1/users/{id}` - Get user
- `PATCH /api/v1/users/{id}` - Update user
- `DELETE /api/v1/users/{id}` - Delete user

## 🚀 Deployment

### Production Checklist

- [ ] Change `SECRET_KEY` to a strong random value
- [ ] Set `ENVIRONMENT=production`
- [ ] Set `DEBUG=False`
- [ ] Configure proper `DATABASE_URL`
- [ ] Set up SSL/TLS certificates
- [ ] Configure CORS origins
- [ ] Set up monitoring and logging
- [ ] Configure backup strategy
- [ ] Set up CI/CD pipeline
- [ ] Review security settings

### Environment Variables

Ensure all sensitive environment variables are properly set in production:
- Use secrets management (AWS Secrets Manager, HashiCorp Vault, etc.)
- Never commit `.env` files to version control
- Use different credentials for each environment

## 📄 License

This project is licensed under the MIT License.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📞 Support

For issues and questions, please open an issue on GitHub.

---

Built with ❤️ using FastAPI
