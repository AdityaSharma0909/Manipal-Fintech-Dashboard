#!/usr/bin/env bash
# =============================================================================
# scripts/run_dev.sh
# Development server startup script.
#
# Usage:
#   chmod +x scripts/run_dev.sh
#   ./scripts/run_dev.sh
#
# What it does:
#   1. Activates the virtual environment (if .venv exists)
#   2. Loads the .env file into shell environment
#   3. Runs Django system checks
#   4. Applies pending migrations
#   5. Starts the development server on 0.0.0.0:8000
#
# For production, use Gunicorn:
#   gunicorn config.wsgi:application --workers 4 --bind 0.0.0.0:8000
# =============================================================================

set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

# --- Activate virtual environment ---
if [ -f ".venv/bin/activate" ]; then
    echo "[run_dev] Activating virtual environment..."
    # shellcheck source=/dev/null
    source ".venv/bin/activate"
elif [ -f "venv/bin/activate" ]; then
    source "venv/bin/activate"
else
    echo "[run_dev] WARNING: No virtual environment found. Using system Python."
fi

# --- Load .env ---
if [ -f ".env" ]; then
    echo "[run_dev] Loading .env..."
    set -a
    # shellcheck source=/dev/null
    source ".env"
    set +a
else
    echo "[run_dev] WARNING: .env file not found. Using existing environment variables."
fi

export DJANGO_SETTINGS_MODULE="config.settings.development"

# --- System check ---
echo "[run_dev] Running Django system checks..."
python manage.py check --deploy 2>/dev/null || true
python manage.py check

# --- Migrations ---
echo "[run_dev] Applying pending migrations..."
python manage.py migrate --run-syncdb

# --- Start server ---
echo "[run_dev] Starting development server on http://0.0.0.0:8000 ..."
python manage.py runserver 0.0.0.0:8000
