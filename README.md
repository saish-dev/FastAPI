# FastAPI Microservices Architecture

Enterprise-grade distributed microservices platform with **auth-service**, **user-service**, and **gateway-service**.

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      API Gateway (8000)                      │
│  • OAuth2/JWT validation                                     │
│  • API Key validation                                        │
│  • Rate limiting                                             │
│  • gRPC client routing                                       │
└───────────────┬─────────────────┬───────────────────────────┘
                │ gRPC:50051      │ gRPC:50052
                ▼                 ▼
    ┌───────────────────┐  ┌───────────────────┐
    │ Auth Service      │  │ User Service      │
    │ (Port 8001)       │  │ (Port 8002)       │
    │ • JWT tokens      │  │ • User CRUD       │
    │ • API keys        │  │ • gRPC client     │
    │ • OAuth2/OIDC     │  │ • Event consumer  │
    └─────────┬─────────┘  └─────────┬─────────┘
              │                       │
              │ Events                │ Events
              ▼                       ▼
    ┌─────────────────────────────────────────┐
    │         NATS (Port 4222)                │
    │  • UserCreated, PasswordChanged         │
    │  • AuthEvent, AuditLogEvent             │
    └─────────────────────────────────────────┘
              │                       │
              ▼                       ▼
    ┌───────────────────┐  ┌───────────────────┐
    │    auth-db        │  │    user-db        │
    │   PostgreSQL      │  │   PostgreSQL      │
    │   (Port 5432)     │  │   (Port 5433)     │
    └───────────────────┘  └───────────────────┘
```

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- Python 3.12+ (for local development)

### Run Everything

```bash
# Start all services
docker compose up --build

# Or use Makefile
make up
```

**Services will be available at:**
- Gateway: http://localhost:8000
- Auth Service: http://localhost:8001
- User Service: http://localhost:8002
- NATS: nats://localhost:4222

### API Documentation
- Gateway Docs: http://localhost:8000/docs
- Auth Docs: http://localhost:8001/docs
- User Docs: http://localhost:8002/docs

## 📦 Technology Stack

### Core
- **Python 3.12**
- **FastAPI** (async web framework)
- **Pydantic v2** (validation)
- **UUIDv7** (primary keys)

### Database
- **SQLAlchemy 2.0** (async ORM)
- **PostgreSQL** (separate per service)
- **Alembic** (migrations)

### Communication
- **gRPC** (synchronous inter-service)
- **NATS** (asynchronous events)
- **Protocol Buffers** (service contracts)

### Security
- **JWT** (access + refresh tokens)
- **API Keys** (service authentication)
- **OAuth2/OIDC** (external IdP support)
- **Bcrypt** (password hashing)

### Observability
- **Structured Logging** (JSON/colored)
- **Correlation ID** propagation
- **Prometheus** metrics
- **OpenTelemetry** (basic)

## 🎯 Services

### Auth Service (Port 8001, gRPC 50051)

**Purpose**: Authentication and authorization

**Features**:
- User registration and login
- JWT access + refresh tokens
- API key generation and validation
- OAuth2/OIDC integration (configurable)
- Event publishing (AuthEvent, AuditLogEvent)

**Endpoints**:
- `POST /auth/register` - Register new user
- `POST /auth/login` - Login with credentials
- `POST /auth/refresh` - Refresh access token
- `POST /auth/api-keys` - Create API key
- `POST /auth/validate-token` - Validate JWT
- `POST /auth/validate-api-key` - Validate API key

**gRPC Methods**:
- `ValidateToken` - Validate JWT token
- `ValidateApiKey` - Validate API key
- `Login` - Authenticate user
- `RefreshToken` - Refresh tokens

**Database**: `auth-db`
- users (credentials, OAuth mappings)
- api_keys (service authentication)
- refresh_tokens (token management)

---

### User Service (Port 8002, gRPC 50052)

**Purpose**: User profile management

**Features**:
- User CRUD operations
- Password management
- gRPC client (calls auth-service)
- Event publishing (UserCreated, PasswordChanged)
- Event consumer (example: AuthEvent)

**Endpoints**:
- `POST /users` - Create user
- `GET /users/{id}` - Get user
- `PUT /users/{id}` - Update user
- `DELETE /users/{id}` - Delete user
- `PUT /users/{id}/password` - Change password

**gRPC Methods**:
- `GetUser` - Get user by ID
- `CreateUser` - Create user
- `UpdateUser` - Update user
- `DeleteUser` - Delete user
- `ChangePassword` - Change password

**Database**: `user-db`
- users (profile data)

---

### Gateway Service (Port 8000)

**Purpose**: API Gateway and routing

**Features**:
- OAuth2/JWT validation
- API Key validation
- Rate limiting (per user/key)
- Circuit breaker (gRPC calls)
- Retry policy
- Correlation ID propagation
- Health aggregation

**Endpoints**:
- `POST /api/auth/*` → auth-service (gRPC)
- `GET/POST/PUT/DELETE /api/users/*` → user-service (gRPC)
- `GET /health` - Aggregated health check

**No Database**: Stateless gateway

## 🔑 Key Features

### UUIDv7 Primary Keys
All services use UUIDv7 for primary keys:
- Time-ordered (better for indexes)
- Globally unique
- No coordination needed
- Better performance than UUIDv4

### gRPC Communication
Services communicate via gRPC:
- Type-safe contracts (Protocol Buffers)
- Better performance than HTTP/JSON
- Automatic code generation
- Built-in load balancing support

### Event-Driven Architecture
Async communication via NATS:
- **UserCreated** - Published when user is created
- **PasswordChanged** - Published when password changes
- **AuthEvent** - Published on login/logout
- **AuditLogEvent** - Published for security events

### Layered Architecture
Each service follows clean architecture:
```
app/
├── core/          # Config, logging, exceptions
├── db/            # Database setup
├── models/        # SQLAlchemy models
├── schemas/       # Pydantic schemas
├── repositories/  # Data access
├── services/      # Business logic
├── routers/       # HTTP endpoints
├── grpc/          # gRPC server/client
└── events/        # Event publisher/consumer
```

### Observability
- **Structured Logging**: JSON format in production
- **Correlation ID**: Propagated across all services
- **Metrics**: Prometheus endpoints
- **Tracing**: OpenTelemetry integration

## 🛠️ Development

### Local Setup

```bash
# Clone repository
git clone <repo-url>
cd FastAPI
git checkout microservice-architecture

# Generate gRPC code
./generate_grpc.sh

# Start services
docker compose up --build
```

### Generate gRPC Code

```bash
chmod +x generate_grpc.sh
./generate_grpc.sh
```

This generates Python code from `.proto` files for all services.

### Run Individual Service

```bash
# Auth service
cd auth-service
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8001

# User service
cd user-service
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8002

# Gateway service
cd gateway-service
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### Database Migrations

```bash
# Auth service
cd auth-service
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head

# User service
cd user-service
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head
```

## 📝 Usage Examples

### 1. Register User

```bash
curl -X POST "http://localhost:8000/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securepass123",
    "full_name": "John Doe"
  }'
```

### 2. Login

```bash
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securepass123"
  }'
```

Response:
```json
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer",
  "expires_in": 1800,
  "user_id": "01933e7a-..."
}
```

### 3. Access Protected Endpoint

```bash
curl -X GET "http://localhost:8000/api/users/01933e7a-..." \
  -H "Authorization: Bearer eyJ..."
```

### 4. Create API Key (for services)

```bash
curl -X POST "http://localhost:8001/auth/api-keys" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer eyJ..." \
  -d '{
    "service_name": "analytics-service",
    "permissions": ["read:users", "write:logs"],
    "expires_in_days": 365
  }'
```

### 5. Use API Key

```bash
curl -X GET "http://localhost:8000/api/users" \
  -H "X-API-Key: your-api-key-here"
```

## 🧪 Testing

### Run Tests

```bash
# All services
make test

# Individual service
cd auth-service
pytest

cd user-service
pytest

cd gateway-service
pytest
```

### gRPC Contract Tests

```bash
cd auth-service
pytest tests/test_grpc.py
```

## 🔒 Security

### JWT Tokens
- **Access Token**: 30 minutes expiration
- **Refresh Token**: 7 days expiration
- **Algorithm**: HS256 (configurable to RS256)

### API Keys
- Hashed with bcrypt before storage
- Per-service permissions
- Configurable expiration
- Last-used tracking

### OAuth2/OIDC
Configure external identity provider:
```env
OAUTH2_ENABLED=true
OAUTH2_ISSUER=https://accounts.google.com
OAUTH2_JWKS_URL=https://www.googleapis.com/oauth2/v3/certs
OAUTH2_CLIENT_ID=your-client-id
OAUTH2_CLIENT_SECRET=your-client-secret
```

## 📊 Monitoring

### Health Checks

```bash
# Gateway (aggregated)
curl http://localhost:8000/health

# Individual services
curl http://localhost:8001/health
curl http://localhost:8002/health
```

### Metrics

```bash
# Prometheus metrics
curl http://localhost:8001/metrics
curl http://localhost:8002/metrics
```

### Logs

```bash
# View logs
docker compose logs -f auth-service
docker compose logs -f user-service
docker compose logs -f gateway-service
```

## 🚀 Deployment

### Production Checklist

- [ ] Change `SECRET_KEY` in all services
- [ ] Enable OAuth2/OIDC if needed
- [ ] Configure proper CORS origins
- [ ] Set `LOG_FORMAT=json`
- [ ] Enable mTLS for gRPC (optional)
- [ ] Set up proper database backups
- [ ] Configure monitoring/alerting
- [ ] Review rate limits
- [ ] Enable HTTPS/TLS

### Environment Variables

See `.env.example` files in each service directory.

## 📚 Project Structure

```
microservices/
├── proto/                    # gRPC definitions
│   ├── common.proto
│   ├── auth.proto
│   └── user.proto
│
├── auth-service/
│   ├── app/
│   │   ├── core/            # Config, logging, security
│   │   ├── db/              # Database setup
│   │   ├── models/          # SQLAlchemy models
│   │   ├── schemas/         # Pydantic schemas
│   │   ├── repositories/    # Data access
│   │   ├── services/        # Business logic
│   │   ├── routers/         # HTTP endpoints
│   │   ├── grpc/            # gRPC server
│   │   └── events/          # NATS publisher
│   ├── alembic/             # Migrations
│   ├── tests/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── .env
│
├── user-service/            # Similar structure
├── gateway-service/         # Similar structure
│
├── docker-compose.yml
├── Makefile
├── generate_grpc.sh
└── README.md
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests
5. Submit a pull request

## 📄 License

MIT License

---

**Built with ❤️ using FastAPI, gRPC, and NATS**
