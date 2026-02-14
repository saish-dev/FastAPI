# FastAPI Layered Architecture Template

A production-ready FastAPI template using **3-Tier Layered Architecture** for building scalable SaaS backends.

## 🏗️ Architecture

This template follows strict **Layered Architecture** (3-tier) principles:

```
app/
├── main.py                 # FastAPI application entry point
│
├── core/                   # Cross-cutting concerns
│   ├── config.py          # Pydantic BaseSettings
│   ├── security.py        # JWT & password hashing
│   ├── logging.py         # Structured logging
│   └── exceptions.py      # Custom exceptions
│
├── db/                     # Database configuration
│   ├── base.py            # SQLAlchemy base
│   └── session.py         # Async session management
│
├── models/                 # SQLAlchemy ORM models
│   └── user.py
│
├── schemas/                # Pydantic schemas
│   ├── auth.py
│   └── user.py
│
├── repositories/           # Data access layer
│   └── user_repository.py
│
├── services/               # Business logic layer
│   ├── auth_service.py
│   └── user_service.py
│
├── routers/                # HTTP layer
│   ├── auth.py
│   └── users.py
│
└── dependencies.py         # Dependency injection
```

## ✨ Features

### Architecture Layers
- ✅ **Router Layer** - HTTP request/response handling only
- ✅ **Service Layer** - Business logic and orchestration
- ✅ **Repository Layer** - Database access and queries
- ✅ **Model Layer** - SQLAlchemy ORM models
- ✅ **Schema Layer** - Pydantic validation models

### Technology Stack
- ✅ **Python 3.12** - Latest Python features
- ✅ **FastAPI** - Modern async web framework
- ✅ **SQLAlchemy 2.0** - Async ORM
- ✅ **PostgreSQL** - Production database
- ✅ **Pydantic v2** - Data validation
- ✅ **Alembic** - Database migrations
- ✅ **JWT** - Authentication (access + refresh tokens)

### DevOps & Testing
- ✅ **Docker & docker-compose** - Containerization
- ✅ **Pytest** - Async testing with fixtures
- ✅ **Pre-commit hooks** - Code quality
- ✅ **Makefile** - Development commands
- ✅ **Structured logging** - JSON/colored output

## 🚀 Quick Start

### Prerequisites
- Python 3.12+
- Docker & Docker Compose
- PostgreSQL (or use Docker)

### Installation

1. **Clone and setup**
```bash
git clone <repository-url>
cd FastAPI
git checkout layered-architecture
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
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
- **API Documentation**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
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

## 🏛️ Layer Responsibilities

### 1. Router Layer (`app/routers/`)
**Responsibility**: HTTP translation only

```python
@router.post("/users/", response_model=UserResponse)
async def create_user(
    user_data: UserCreate,
    user_service: UserService = Depends(get_user_service),
) -> UserResponse:
    """HTTP handling only - delegates to service layer."""
    return await user_service.create_user(user_data)
```

### 2. Service Layer (`app/services/`)
**Responsibility**: Business logic and orchestration

```python
class UserService:
    async def create_user(self, user_data: UserCreate) -> UserResponse:
        """Business logic - validation, orchestration."""
        # Check if user exists
        existing = await self.repository.get_by_email(user_data.email)
        if existing:
            raise ConflictError("User already exists")
        
        # Create user
        user = User(email=user_data.email, ...)
        created = await self.repository.create(user)
        return UserResponse.model_validate(created)
```

### 3. Repository Layer (`app/repositories/`)
**Responsibility**: Database access only

```python
class UserRepository:
    async def get_by_email(self, email: str) -> User | None:
        """Database query only - no business logic."""
        result = await self.db.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()
```

## 📊 API Endpoints

### Authentication
- `POST /api/auth/login` - Login with email/password
- `POST /api/auth/refresh` - Refresh access token

### Users
- `POST /api/users/` - Create user (public)
- `GET /api/users/me` - Get current user (protected)
- `GET /api/users/{id}` - Get user by ID (protected)
- `GET /api/users/` - List users (protected)
- `PUT /api/users/{id}` - Update user (protected)
- `DELETE /api/users/{id}` - Delete user (protected)

### System
- `GET /health` - Health check
- `GET /docs` - Swagger UI
- `GET /redoc` - ReDoc

## 🔐 Authentication

### Create User
```bash
curl -X POST "http://localhost:8000/api/users/" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securepassword123",
    "full_name": "John Doe"
  }'
```

### Login
```bash
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securepassword123"
  }'
```

### Access Protected Endpoint
```bash
curl -X GET "http://localhost:8000/api/users/me" \
  -H "Authorization: Bearer <access_token>"
```

## 🧪 Testing Strategy

### API Tests
Test HTTP endpoints with test database:
```python
def test_create_user(client):
    response = client.post("/api/users/", json={...})
    assert response.status_code == 201
```

### Service Tests
Test business logic with mocked repositories:
```python
async def test_user_service_create():
    service = UserService(mock_repository)
    user = await service.create_user(user_data)
    assert user.email == user_data.email
```

### Repository Tests
Test database operations:
```python
async def test_user_repository_get_by_email(db_session):
    repo = UserRepository(db_session)
    user = await repo.get_by_email("test@example.com")
    assert user is not None
```

## 🚢 Deployment

### Docker Production Build

```bash
docker build -t fastapi-layered:latest .
docker run -p 8000:8000 --env-file .env fastapi-layered:latest
```

### Environment Variables for Production

```env
ENVIRONMENT=production
DEBUG=false
LOG_FORMAT=json
DATABASE_URL=postgresql+asyncpg://...
SECRET_KEY=<generate-secure-key>
```

## 🔧 Configuration

All configuration is managed through environment variables (see `.env.example`):

```env
# Database
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/db

# Security
SECRET_KEY=your-secret-key-change-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# CORS
CORS_ORIGINS=["http://localhost:3000"]
```

## 📚 Project Structure Explained

```
app/
├── core/           # Shared utilities (config, security, logging)
├── db/             # Database setup (base, session)
├── models/         # SQLAlchemy models (database tables)
├── schemas/        # Pydantic models (validation, serialization)
├── repositories/   # Data access (SQL queries)
├── services/       # Business logic (orchestration, validation)
├── routers/        # HTTP endpoints (request/response)
├── dependencies.py # Dependency injection
└── main.py         # Application entry point
```

## 🎯 Key Design Principles

### 1. Separation of Concerns
- Each layer has a single, well-defined responsibility
- No business logic in routers
- No HTTP handling in services
- No business logic in repositories

### 2. Dependency Injection
- Services depend on repositories (injected)
- Routers depend on services (injected)
- Easy to test with mocks

### 3. Async All the Way
- Async SQLAlchemy for database
- Async FastAPI for HTTP
- Non-blocking I/O throughout

### 4. Type Safety
- Pydantic for validation
- Type hints everywhere
- MyPy for static type checking

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and linters
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details

---

**Built with ❤️ using FastAPI and Layered Architecture principles**
