# Radian Finserv — Full-Stack Gold Loan & Lending Fintech Platform

Welcome to the **Radian Finserv** (Manipal Fintech Analytics) repository. This project is a production-oriented, full-stack financial platform facilitating gold loan lending, customer onboarding, credit bureau checks, and analytics.

---

## Repository Structure

The repository is organized into three main application layers:

```text
radian-finserv/
├── Frontend/         # Core Customer React Application (React 19 + Vite + TypeScript)
├── mf_dashboard/     # Internal Admin Analytics Dashboard (React 19 + Vite + TypeScript + React Query)
├── mf_backend/       # Django REST Framework Backend API (Django 4 + PostgreSQL + Celery + Elasticsearch)
├── .gitignore        # Global repository ignore configurations
├── .env.example      # Root environment settings reference
└── README.md         # This repository documentation
```

---

## System Architecture

```text
   Frontend React Client           Internal React Dashboard
            │                                 │
            └──────────────┬──────────────────┘
                           │ HTTPS (API requests)
                           ▼
                    Django REST API (mf_backend)
                           │
             ┌─────────────┼─────────────┬─────────────┐
             ▼             ▼             ▼             ▼
        PostgreSQL       Redis     Elasticsearch    MinIO/S3
                           │
                           ▼
                     Celery Worker (Background tasks & reports)
                           │
                           ▼
                     Celery Beat (Job scheduler)
```

---

## Security Guidelines

This repository is configured with a zero-secrets commit policy.
*   All private keys (`*.key`, `*.pem`), credentials (`*.p12`, `*.pfx`, `*adminsdk.json`), keystores (`*.jks`), and SQL database dumps (`*.sql`) are globally ignored by `.gitignore`.
*   Never check active passwords, tokens, or credentials into source control.
*   Always load configuration variables via the environment from `.env` files.

---

## Local Development Setup

### 1. Environment Configurations
Copy the `.env.example` templates in each folder to their respective `.env` files and populate local variables:
*   `cp mf_backend/.env.example mf_backend/.env`
*   `cp Frontend/.env.example Frontend/.env`
*   `cp mf_dashboard/.env.example mf_dashboard/.env`

### 2. Backend Server (`mf_backend/`)
Ensure PostgreSQL, Redis, and Elasticsearch are running locally, then:
```bash
cd mf_backend
# Activate virtual environment
source .venv/bin/activate   # Linux/macOS
.venv\Scripts\activate      # Windows

# Run migrations and start server
python manage.py migrate
python manage.py runserver 8000
```
To run Celery tasks:
```bash
# Celery Worker
celery -A radian_backend worker -l info

# Celery Beat (Scheduler)
celery -A radian_backend beat -l info -s celery/celerybeat-schedule
```

### 3. Core Frontend (`Frontend/`)
```bash
cd Frontend
npm install
npm run dev
```

### 4. Admin Dashboard (`mf_dashboard/`)
```bash
cd mf_dashboard
npm install
npm run dev
```

---

## Deployment Blueprint

### Frontends
*   **Hosting:** Hosted natively on **Vercel** as two separate project environments.
*   **Fallback Handling:** Both folders contain `vercel.json` rewrite configurations to ensure SPA paths redirect correctly to `/index.html` on browser refreshes.

### Backend Application
*   **Hosting:** Django and Celery workers are hosted on virtual machines or container hosts (such as DigitalOcean, AWS ECS, or Render) due to long-running task executors and deep system library dependencies (Ghostscript, ImageMagick, Playwright).
*   **Databases:** Utilize managed instances for PostgreSQL (with connection pooling) and Redis, and standard managed Elasticsearch.
