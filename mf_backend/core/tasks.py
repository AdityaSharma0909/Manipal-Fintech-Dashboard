# tasks.py
from celery import shared_task
from core.service.database_backup import BackDatabase
from core.service.database_transfer import DatabaseTransfer


@shared_task(name='backup_database')
def backup_database():
    BackDatabase().backup()


@shared_task(name='backup_production_database')
def backup_production_database():
    """Create a dump on the production server."""
    return DatabaseTransfer().backup_production_database()


@shared_task(name='download_production_database_backup')
def download_production_database_backup():
    """Download the latest completed production dump onto the development server."""
    return DatabaseTransfer().download_latest_production_backup()
