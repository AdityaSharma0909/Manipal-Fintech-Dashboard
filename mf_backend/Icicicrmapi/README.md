# ICICI CRM Backend

Enterprise-grade Django + PostgreSQL backend for the ICICI CRM service.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.12+ |
| Framework | Django 5+ |
| API | Django REST Framework |
| Database | PostgreSQL |
| Authentication | JWT (custom, via PyJWT) |
| HTTP Client | httpx |
| Retry Logic | Tenacity |
| Encryption | cryptography (Fernet) |
| Logging | Python logging (structured JSON in prod) |
| Config | python-decouple + .env |

---

## Architecture

```
Request → API Layer → Business Layer → Data Layer → PostgreSQL
                   → Business Layer → Utility Layer → ICICI CRM API
```

### Layer Responsibilities

| Layer | Location | Responsibility |
|---|---|---|
| **API** | `apps/api/` | HTTP request/response handling, serialization, routing |
| **Business** | `apps/business/services/` | Business logic, orchestration, workflow |
| **Data** | `apps/data/repositories/` | ORM queries, database access |
| **Models** | `apps/models/` | Django ORM model definitions |
| **Utilities** | `apps/utilities/` | Reusable helpers (logging, encryption, HTTP, date) |
| **Integrations** | `apps/integrations/icici/` | ICICI CRM external API client |
| **Auth** | `apps/authentication/` | JWT backend, permissions |
| **Validators** | `apps/validators/` | Request + domain validation |
| **Middleware** | `apps/middleware/` | Correlation ID, request logging, exception handling |
| **Common** | `apps/common/` | Shared exceptions, responses, DTOs, constants |

---

## Project Structure

```
icici_crm_backend/
│
├── apps/
│   ├── api/
│   │   └── v1/
│   │       ├── urls.py          # v1 URL routing
│   │       └── views.py         # HealthCheckView + BaseAPIView
│   │
│   ├── authentication/
│   │   ├── backends.py          # JWTAuthentication (DRF backend)
│   │   ├── jwt_handler.py       # Token pair creation, refresh, revoke
│   │   └── permissions.py       # IsAdminUser, HasRole, IsOwnerOrAdmin
│   │
│   ├── business/
│   │   └── services/
│   │       └── base_service.py  # BaseService (all services inherit this)
│   │
│   ├── common/
│   │   ├── constants/
│   │   │   ├── app_constants.py  # App-wide enums and constants
│   │   │   ├── error_codes.py    # Centralised error code registry
│   │   │   └── status_codes.py   # HTTP + BizStatus codes
│   │   ├── dtos/
│   │   │   └── base_dto.py       # RequestDTO / ResponseDTO base classes
│   │   ├── exceptions/
│   │   │   ├── base_exception.py        # CRMBaseException + domain exceptions
│   │   │   ├── http_exceptions.py       # HTTP-layer exceptions (views only)
│   │   │   └── integration_exceptions.py # ICICI integration exceptions
│   │   └── responses/
│   │       ├── api_response.py   # ApiResponse (success envelope)
│   │       └── error_response.py # ErrorResponse (error envelope)
│   │
│   ├── data/
│   │   └── repositories/
│   │       └── base_repository.py # BaseRepository[Model] with generic CRUD
│   │
│   ├── integrations/
│   │   └── icici/
│   │       ├── base_client.py   # ICICIBaseClient (all ICICI calls go here)
│   │       └── endpoints.py     # URL registry for all ICICI CRM endpoints
│   │
│   ├── middleware/
│   │   ├── correlation_id.py    # Assigns X-Correlation-ID to every request
│   │   ├── exception_handler.py # Catch-all for unhandled exceptions → JSON 500
│   │   └── request_logging.py   # Structured request/response logger
│   │
│   ├── models/
│   │   └── base_model.py        # BaseModel (UUID PK, timestamps, soft-delete)
│   │
│   ├── utilities/
│   │   ├── logger.py            # get_logger(), JsonFormatter, ContextLogger
│   │   ├── encryption.py        # Fernet encrypt/decrypt for PII fields
│   │   ├── token_handler.py     # Low-level JWT encode/decode primitives
│   │   ├── retry_handler.py     # @with_retry decorator (Tenacity)
│   │   ├── http_client.py       # httpx wrapper with timeout + correlation ID
│   │   ├── date_utils.py        # UTC/IST conversion, date formatting
│   │   └── string_utils.py      # PAN/mobile/email masking, sanitization
│   │
│   └── validators/
│       ├── base_validator.py    # BaseValidator + field helpers (mobile, PAN, email)
│       └── request_validator.py # Request-level validation (headers, pagination)
│
├── config/
│   ├── settings/
│   │   ├── base.py              # Shared settings (DB, DRF, JWT, Logging, Middleware)
│   │   ├── development.py       # Dev overrides (DEBUG=True, SQL logging)
│   │   └── production.py        # Prod overrides (HTTPS, security hardening)
│   ├── urls.py                  # Root URL config (mounts /api/v1/)
│   ├── wsgi.py                  # WSGI entry point (Gunicorn)
│   └── asgi.py                  # ASGI entry point (Uvicorn/Daphne)
│
├── logs/                        # Log file output (gitignored, .gitkeep tracked)
│
├── requirements/
│   ├── base.txt                 # Shared dependencies
│   ├── development.txt          # Dev-only (pytest, debug toolbar, etc.)
│   └── production.txt           # Prod-only (gunicorn, django-storages, etc.)
│
├── scripts/
│   ├── run_dev.sh               # Dev server startup script
│   └── seed_data.py             # Idempotent database seeder
│
├── manage.py                    # Django management entry point
├── pytest.ini                   # pytest configuration
├── setup.cfg                    # flake8, isort, mypy, coverage config
├── .env                         # Local dev secrets (gitignored)
└── .env.example                 # Environment template (committed)
```

---

## Quick Start

### 1. Clone & setup virtual environment

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements/development.txt
```

### 3. Configure environment

```bash
cp .env.example .env
# Edit .env and fill in your PostgreSQL credentials and secrets
```

### 4. Setup PostgreSQL database

```bash
# Create the database (one-time):
psql -U postgres -c "CREATE DATABASE icici_crm_dev;"
```

### 5. Run migrations

```bash
python manage.py migrate
```

### 6. Seed development data

```bash
python scripts/seed_data.py
```

### 7. Start the development server

```bash
python manage.py runserver
# OR
./scripts/run_dev.sh
```

Server runs at: **http://localhost:8000**

Health check: **GET http://localhost:8000/api/v1/health/**

---

## API Versioning

All APIs are versioned at the URL path level:

```
/api/v1/...   ← Current version
/api/v2/...   ← Future version (add new apps/api/v2/ package)
```

---

## Environment Variables

See `.env.example` for the full list. Key variables:

| Variable | Description |
|---|---|
| `DJANGO_ENV` | `development` / `production` |
| `SECRET_KEY` | Django secret key |
| `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT` | PostgreSQL connection |
| `JWT_SECRET_KEY` | JWT signing secret |
| `ICICI_CRM_BASE_URL` | ICICI CRM API base URL |
| `ICICI_CRM_API_KEY` | ICICI CRM API authentication key |
| `ENCRYPTION_KEY` | Fernet key for PII field encryption |
| `LOG_LEVEL` | `DEBUG` / `INFO` / `WARNING` / `ERROR` |

---

## Naming Conventions

| Type | Convention | Example |
|---|---|---|
| Files | `snake_case.py` | `base_service.py` |
| Classes | `PascalCase` | `CustomerService` |
| Functions/methods | `snake_case` | `get_customer_by_id()` |
| Constants | `UPPER_SNAKE_CASE` | `MAX_RETRY_COUNT` |
| URL names | `v1:<resource>-<action>` | `v1:customer-detail` |
| Error codes | `LAYER_DESCRIPTION` | `VAL_INVALID_MOBILE` |
| Django apps | `snake_case` | `apps/business/services/` |

---

## Adding a New Domain

When a new file is provided, follow this checklist:

1. **Model** → `apps/models/<domain>_model.py` (extends `BaseModel`)
2. **Repository** → `apps/data/repositories/<domain>_repository.py` (extends `BaseRepository`)
3. **Service** → `apps/business/services/<domain>_service.py` (extends `BaseService`)
4. **Serializer** → `apps/api/v1/<domain>_serializers.py` (DRF Serializer)
5. **View** → `apps/api/v1/<domain>_views.py` (extends `BaseAPIView`)
6. **URLs** → Register in `apps/api/v1/urls.py`
7. **Validator** → `apps/validators/<domain>_validator.py` (extends `BaseValidator`)
8. **ICICI Client** → `apps/integrations/icici/<domain>_client.py` (extends `ICICIBaseClient`)
9. **Migration** → `python manage.py makemigrations && python manage.py migrate`
10. **Tests** → `tests/<domain>/`

---

## Running Tests

```bash
pytest                          # Run all tests
pytest -m unit                  # Unit tests only
pytest -m api                   # API tests only
pytest --cov=apps --cov-report=html  # With coverage report
```

---

## Logging

- **Development**: Human-readable text format, `DEBUG` level, console output.
- **Production**: Structured JSON format, `INFO` level, file + console.
- Log files: `logs/icici_crm.log` (gitignored, `.gitkeep` tracked).
- Correlation ID is automatically embedded in every log line.

---

## Security

- JWT access tokens expire in 60 minutes (configurable).
- All PII fields (PAN, Aadhaar, mobile) must be encrypted via `apps/utilities/encryption.py`.
- No raw secrets in code — use `.env` / environment variables.
- HTTPS enforced in production via `SECURE_SSL_REDIRECT = True`.
