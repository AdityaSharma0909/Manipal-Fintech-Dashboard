from __future__ import absolute_import
import os

from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'radian_backend.settings')
app = Celery('radian_backend')
app.config_from_object('django.conf:settings')
app.autodiscover_tasks()

app_env = os.environ.get('APP_ENV', '').strip().upper()

app.conf.beat_schedule = {

    # get gold price from webiste "https://ibjarates.com/"
    # 'fetch_gold_price': {
    #     'task': 'get_gold_price',
    #     'schedule': crontab(hour=0, minute=0, day_of_week='mon,tue,wed,thu,fri'),
        
    # },
    'run_loan_calculation': {
        'task': 'loan_payment_jobs',
        # 'schedule': crontab(hour=0, minute=0,day_of_week='mon,tue,wed,thu,fri,sat,sun'),
        # TODO: correct time
        'schedule': crontab(hour=18, minute=22, day_of_week='mon,tue,wed,thu,fri,sat,sun'),

    },
    'mail_mis_report': {
        #THis report is only sent on UAT server
        'task': 'export_application_data',
        # 'schedule': crontab(hour=0, minute=0,day_of_week='mon,tue,wed,thu,fri,sat,sun'),
        # TODO: correct time
        'schedule': crontab(hour=0, minute=0, day_of_week='mon,tue,wed,thu,fri,sat'),

    },
    'export_daily_timestamps_report': {
        'task': 'export_today_timestamps_task',
        'schedule': crontab(hour=12, minute=45, day_of_week='mon,tue,wed,thu,fri,sat,sun'),
    },
    'auto_close_leads_daily': {
        'task': 'onboarding_v2.tasks.auto_close_leads_task',
        'schedule': crontab(hour=14, minute=21, day_of_week='mon,tue,wed,thu,fri,sat,sun'),
    },
    'export_banca_leads_hourly': {
        'task': 'onboarding_v2.tasks.export_banca_leads_hourly_task',
        'schedule': crontab(hour='9-19', minute=0),  # Runs every hour from 9 AM to 7 PM
        # 'schedule': crontab(minute='*/2'),
        
    },
    'export_multi_table_report_twice_daily': {
        'task': 'onboarding_v2.tasks.export_multi_table_report_task',
        'schedule': crontab(hour='8,18', minute=0),
        # 'schedule': crontab(minute='*/2'),
    },
    'export_bank_crm_report_daily': {
        'task': 'onboarding_v2.tasks.export_bank_crm_report_task',
        'schedule': crontab(hour=19, minute=0),
        # 'schedule': crontab(minute='*/2'),
    },
    'export_bt_disbursal_report_daily': {
        'task': 'onboarding_v2.tasks.export_bt_disbursal_report_task',
        'schedule': crontab(hour=19, minute=30),
        # 'schedule': crontab(minute='*/2'),

    },
    'export_new_gl_against_bt_report_daily': {
        'task': 'onboarding_v2.tasks.export_new_gl_against_bt_report_task',
        'schedule': crontab(hour=19, minute=45),
        # 'schedule': crontab(minute='*/2'),

    },
    'export_tele_centre_report_daily': {
        'task': 'onboarding_v2.tasks.export_tele_centre_report_task',
        'schedule': crontab(hour=13, minute=15),
        # 'schedule': crontab(minute='*/2'),
    },
    # 'postgresql_database_backup':{
    #     'task':'backup_database',
    #     'schedule': crontab(hour=18, minute=20, day_of_week='mon,tue,wed,thu,fri,sat,sun'),
    #
    # }
    # 'backup_production_database' : {
    #     'task': 'backup_production_database',
    #     'schedule': crontab(minute='*/2'),
    # }
}

# Each server receives only the job appropriate for its environment. The task
# itself also checks APP_ENV, so an incorrectly routed task fails safely.
# if app_env == 'PROD':
#     app.conf.beat_schedule['backup_production_database'] = {
#         'task': 'backup_production_database',
#         'schedule': crontab(hour=18, minute=20),
#     }
# elif app_env == 'DEV':
#     app.conf.beat_schedule['download_production_database_backup'] = {
#         'task': 'download_production_database_backup',
#         # Allow the production dump to finish before looking for the newest file.
#         'schedule': crontab(hour=19, minute=20),
#         'schedule': crontab(minute='*/2'),
        
# #     }
