from celery import shared_task

from utils.envSetup import environment
from .services.mail_reports_data import MailExportData


@shared_task(name='export_application_data')
def export_application():
    env=environment.APP_ENV
    if env=='PROD':
        MailExportData().process()