import traceback

from django.core.mail import EmailMessage, send_mail

from utility.background_tasks import BackgroundTask
from utils.envSetup import environment


class EmailReport(BackgroundTask):

    def __init__(self):
        super().__init__()


    def process(self, **kwargs):
        try:
            send_mail(subject=kwargs.get('subject'), message=kwargs.get('message'), from_email=environment.DEFAULT_FROM_EMAIL,
                      recipient_list=['saif.k@getafixtechnologies.com','asif@getafixtechnologies.com',
                                      'kartik.patel@getafixtechnologies.com'])
        except Exception:
            traceback.print_exc()

