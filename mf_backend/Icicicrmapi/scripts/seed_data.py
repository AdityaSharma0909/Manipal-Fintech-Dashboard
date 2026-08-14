#!/usr/bin/env python
"""
scripts/seed_data.py
======================
Development database seeding script.

Purpose:
  - Populate the local PostgreSQL database with realistic seed data for development.
  - Does NOT run in production (guard checks DJANGO_ENV).
  - Idempotent: running it multiple times produces the same state (no duplicates).

Usage:
    # With virtual environment activated:
    DJANGO_SETTINGS_MODULE=config.settings.development python scripts/seed_data.py

What it seeds (add sections as models are created):
  - Admin superuser
  - Sample users with roles

Run order:
  1. Ensure DB is migrated: python manage.py migrate
  2. Run this script:       python scripts/seed_data.py
"""

import os
import sys
import django

# ---------------------------------------------------------------------------
# Bootstrap Django before importing models
# ---------------------------------------------------------------------------
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.development")
django.setup()

# ---------------------------------------------------------------------------
# Safety guard — refuse to run in production
# ---------------------------------------------------------------------------
from django.conf import settings  # noqa: E402

DJANGO_ENV = os.getenv("DJANGO_ENV", "development").lower()
if DJANGO_ENV == "production":
    print("[seed_data] ERROR: Seeding is not allowed in production environment.")
    sys.exit(1)

# ---------------------------------------------------------------------------
# Imports (after Django setup)
# ---------------------------------------------------------------------------
from django.contrib.auth import get_user_model  # noqa: E402

User = get_user_model()

print("[seed_data] Starting seed process...")
print(f"[seed_data] Environment : {DJANGO_ENV}")
print(f"[seed_data] Database    : {settings.DATABASES['default']['NAME']}")
print()


# ---------------------------------------------------------------------------
# Seed: Admin superuser
# ---------------------------------------------------------------------------
def seed_admin_user():
    email = "admin@icicicrm.local"
    if User.objects.filter(email=email).exists():
        print(f"  [SKIP] Admin user already exists: {email}")
        return

    User.objects.create_superuser(
        username="admin",
        email=email,
        password="Admin@12345",  # Change immediately after first login
    )
    print(f"  [OK]   Admin superuser created: {email} / Admin@12345")


# ---------------------------------------------------------------------------
# Seed: Sample staff users
# ---------------------------------------------------------------------------
def seed_sample_users():
    sample_users = [
        {"username": "manager01", "email": "manager01@icicicrm.local", "password": "Manager@12345"},
        {"username": "agent01",   "email": "agent01@icicicrm.local",   "password": "Agent@12345"},
    ]
    for u in sample_users:
        if User.objects.filter(email=u["email"]).exists():
            print(f"  [SKIP] User already exists: {u['email']}")
            continue
        User.objects.create_user(**u)
        print(f"  [OK]   User created: {u['email']}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    print("[seed_data] Seeding admin user...")
    seed_admin_user()

    print("[seed_data] Seeding sample users...")
    seed_sample_users()

    # ---- Add more seed functions here as models are added ----
    # seed_leads()
    # seed_customers()
    # seed_policies()

    print()
    print("[seed_data] Seed complete.")


if __name__ == "__main__":
    main()
