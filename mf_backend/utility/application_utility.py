from application.models import Application

from datetime import datetime


class ApplicationUtils:
    def generate_application_number(self, app: Application):

        # n = datetime.now()
        # n.strftime('%m')
        # n.strftime('%Y')}
        

        return f"{app.branch.branch_code}"
        