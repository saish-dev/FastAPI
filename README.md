# FastAPI DDD/Clean Architecture Template

A production-ready FastAPI template implementing **Domain-Driven Design (DDD)** and **Clean Architecture** principles with advanced patterns for enterprise applications.

## 🏗️ Architecture

This template follows strict **Clean Architecture** and **DDD** principles:

```
app/
├── domain/              # Pure business logic (NO framework dependencies)
│   ├── shared/          # Base classes (Entity, ValueObject, DomainEvent)
│   └── users/           # User aggregate
│       ├── entities.py      # User entity (aggregate root)
│       ├── value_objects.py # Email value object
│       ├── events.py        # Domain events
│       ├── repository.py    # Abstract repository interface
│       └── exceptions.py    # Domain exceptions
│
├── application/         # Use cases and orchestration
│   └── users/
│       ├── dto.py           # Data transfer objects
│       ├── commands.py      # Write operations (CQRS)
│       ├── queries.py       # Read operations (CQRS)
│       ├── use_cases.py     # Application services
│       └── unit_of_work.py  # UoW interface
│
├── infrastructure/      # Framework implementations
│   ├── db/              # SQLAlchemy models and session
│   ├── repositories/    # Repository implementations
│   ├── events/          # Event bus and outbox pattern
│   ├── cache/           # Redis cache layer
│   └── auth/            # JWT and password hashing
│
├── api/                 # HTTP layer
│   └── v1/
│       └── users.py     # User endpoints
│
└── core/                # Cross-cutting concerns
    ├── config.py        # Pydantic settings
    ├── logging.py       # Structured logging
    ├── exceptions.py    # Exception handlers
    └── middleware.py    # Custom middleware
```

## ✨ Features

### Core Patterns
- ✅ **Domain-Driven Design (DDD)** - Entities, Value Objects, Aggregates
- ✅ **Clean Architecture** - Strict layer separation with dependency inversion
- ✅ **CQRS** - Command/Query separation
- ✅ **Repository Pattern** - Abstract data access
- ✅ **Unit of Work** - Transaction management
- ✅ **Event Bus** - Domain event publishing
- ✅ **Outbox Pattern** - Reliable event delivery

### Technology Stack
- ✅ **Python 3.12** - Latest Python features
- ✅ **FastAPI** - Modern async web framework
- ✅ **SQLAlchemy 2.0** - Async ORM
- ✅ **PostgreSQL** - Production database
- ✅ **Redis** - Caching layer
- ✅ **Celery** - Background task processing
- ✅ **Pydantic v2** - Data validation
- ✅ **Alembic** - Database migrations
- ✅ **JWT** - Authentication

### DevOps & Testing
- ✅ **Docker & docker-compose** - Containerization
- ✅ **Pytest** - Async testing
- ✅ **GitHub Actions** - CI/CD pipeline
- ✅ **Pre-commit hooks** - Code quality
- ✅ **Makefile** - Development commands

## 🚀 Quick Start

### Prerequisites
- Python 3.12+
- Docker & Docker Compose
- PostgreSQL (or use Docker)
- Redis (or use Docker)

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd FastAPI
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
make dev-install
```

4. **Configure environment**
```bash
cp .env.example .env
# Edit .env and set your configuration
```

5. **Start services with Docker**
```bash
make docker-up
```

6. **Run migrations**
```bash
make migrate
```

7. **Start development server**
```bash
make run
```

Visit:
- **API Documentation**: http://localhost:8000/api/docs
- **ReDoc**: http://localhost:8000/api/redoc
- **Health Check**: http://localhost:8000/health

## 📝 Development

### Available Commands

```bash
make help           # Show all available commands
make install        # Install production dependencies
make dev-install    # Install development dependencies
make run            # Run development server
make test           # Run tests
make test-cov       # Run tests with coverage
make lint           # Run linters
make format         # Format code
make migrate        # Run database migrations
make migration      # Create new migration
make docker-up      # Start Docker services
make docker-down    # Stop Docker services
make clean          # Clean cache files
```

### Creating a Migration

```bash
make migration msg="add user table"
make migrate
```

### Running Tests

```bash
# Run all tests
make test

# Run with coverage
make test-cov

# Run specific test
pytest tests/test_api.py::test_create_user
```

## 🏛️ Architecture Principles

### 1. Dependency Rule
- **Domain** depends on nothing
- **Application** depends on Domain
- **Infrastructure** depends on Domain & Application
- **API** depends on Application

### 2. Domain Layer (Pure Business Logic)
```python
# NO framework dependencies!
from app.domain.users.entities import User
from app.domain.users.value_objects import Email

# Create user with domain logic
email = Email("user@example.com")
user = User.create(email=email, hashed_password="...")

# Domain events are raised automatically
events = user.get_domain_events()  # [UserCreated(...)]
```

### 3. Application Layer (Use Cases)
```python
# Orchestrates domain logic
from app.application.users.use_cases import UserUseCases
from app.application.users.commands import CreateUserCommand

# Use case coordinates the operation
command = CreateUserCommand(email="user@example.com", password="...")
user_dto = await use_cases.create_user(command)
```

### 4. Infrastructure Layer (Implementations)
```python
# Implements domain interfaces
from app.infrastructure.repositories.user_repository import UserRepository
from app.domain.users.repository import IUserRepository

# Repository implements domain interface
repository: IUserRepository = UserRepository(session)
user = await repository.get_by_email(email)
```

## 🔧 Configuration

All configuration is managed through environment variables (see `.env.example`):

```env
# Database
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/db

# Redis
REDIS_URL=redis://localhost:6379/0

# Security
SECRET_KEY=your-secret-key-change-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Celery
CELERY_BROKER_URL=redis://localhost:6379/1
```

## 📊 API Endpoints

### Users
- `POST /api/v1/users/` - Create user
- `GET /api/v1/users/{id}` - Get user by ID
- `GET /api/v1/users/` - List users
- `PUT /api/v1/users/{id}` - Update user
- `DELETE /api/v1/users/{id}` - Delete user
- `POST /api/v1/users/{id}/activate` - Activate user
- `POST /api/v1/users/{id}/deactivate` - Deactivate user

### System
- `GET /health` - Health check
- `GET /api/docs` - Swagger UI
- `GET /api/redoc` - ReDoc

## 🧪 Testing Strategy

### Domain Tests
Test pure business logic without any framework dependencies:
```python
def test_user_creation():
    email = Email("test@example.com")
    user = User.create(email=email, hashed_password="...")
    assert user.email == email
    assert len(user.get_domain_events()) == 1
```

### Application Tests
Test use cases with mocked repositories:
```python
async def test_create_user_use_case():
    # Test orchestration logic
    command = CreateUserCommand(...)
    user_dto = await use_cases.create_user(command)
    assert user_dto.email == command.email
```

### API Tests
Test HTTP endpoints with test database:
```python
def test_create_user_endpoint(client):
    response = client.post("/api/v1/users/", json={...})
    assert response.status_code == 201
```

## 🚢 Deployment

### Docker Production Build

```bash
docker build -t fastapi-ddd:latest .
docker run -p 8000:8000 --env-file .env fastapi-ddd:latest
```

### Environment Variables for Production

```env
ENVIRONMENT=production
DEBUG=false
LOG_FORMAT=json
DATABASE_URL=postgresql+asyncpg://...
SECRET_KEY=<generate-secure-key>
```

## 📚 Key Patterns Explained

### Domain Events
Events are raised when important business actions occur:
```python
user.activate()  # Raises UserActivated event
events = user.get_domain_events()
```

### Unit of Work
Manages transactions and coordinates repositories:
```python
async with uow:
    user = await uow.users.get_by_id(user_id)
    user.activate()
    await uow.users.save(user)
    await uow.commit()  # Events published after commit
```

### Event Bus
Decouples aggregates through events:
```python
event_bus.subscribe(UserCreated, send_welcome_email_handler)
await event_bus.publish(UserCreated(...))
```

### Outbox Pattern
Ensures reliable event delivery:
- Events stored in database table
- Published after transaction commit
- Prevents lost events

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and linters
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details

## 🙏 Acknowledgments

This template implements patterns from:
- **Domain-Driven Design** by Eric Evans
- **Clean Architecture** by Robert C. Martin
- **Implementing Domain-Driven Design** by Vaughn Vernon

---

**Built with ❤️ using FastAPI, SQLAlchemy, and Clean Architecture principles**
