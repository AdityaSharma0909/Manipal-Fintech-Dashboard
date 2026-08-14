import datetime
from io import BytesIO
import pandas as pd
from django.core.mail import EmailMessage

from application.services.export_application_data import ExportApplicationService
from utils.envSetup import environment


class MailExportData:


    def process(self, ):
        data=ExportApplicationService().get_application_data(query_options=[])
        columns=['Name','Email','Gender','DOB','Contact Number',
                                                      'Occupation','Net Annual Income','Aadhar No','PAN',
                                                      "Mother's Name","Father's Name","Spouse's Name",'Education',
                                                      'Religion','Nationality','Caste','Bank Name',
                                                      'Account Number','IFSC code','Account Holder Name','Branch Code','Branch Name','Branch State','Status',
                                                      'Application number','Purpose of loan','Loan amount','Contra loan amount','Product name',
                                                      'Lender name','White goods','Total goods price','Total weight',
                                                      'Net weight','Application type','Takeover Lender Name','Takeover Loan Amount','Takeover Requested Amount','Takeover Total Release Amount','Takeover Loan Start Date','Takeover Maturity Date','Takeover Loan Reference Number','Takeover Gold Weight Pledged','Originated by name',
                                                      'Appraised by name','Nominee Name','Nominee Age','Nominee Relation','Nominee Contact','Tenure','Intrest rate','Processing fee',
                                                      'Processing fee percent','Amortization type','Penalty','GST',
                                                      'Stamp duty','Ltv','Gold rate(per gram)','Disbursal Amount','Disbursed date',
                                                      'Account Created At']
        columns_with_zero=['Loan amount', 'Total weight', 'Net weight', 'Tenure' , 'Contra loan amount' , 'Total goods price' , 'Gold rate(per gram)' , 'Ltv' , 'Stamp duty' , 'Intrest rate' , 'Processing fee' , 'Penalty' , 'Disbursal Amount' , 'GST' ]

        excel_buffer=self.generate_excel_sheet(data, columns, columns_with_zero)
        self.send_mail(excel_buffer)

    def send_mail(self, excel_buffer):
        excel_buffer.seek(0)
        email_subject = 'Radian Application MIS Report'
        email_body = f"""Hi Team,\n\nPlease find the Application MIS report attached to this email. This report was generated today at {datetime.datetime.today().time()}.\n\nThanks & Regards
        """
        from_email = environment.EMAIL_HOST_USER
        to_email = 'saif.k@getafixtechnologies.com'

        email = EmailMessage(email_subject, email_body, from_email, [to_email,'kartik.patel@getafixtechnologies.com','asif@getafixtechnologies.com','lavanya.byanna@radianfinserv.com', str(environment.DEFAULT_CPC_ADMIN_EMAIL)])
        email.attach(f'Application MIS Report_{datetime.datetime.today().date()}_{datetime.datetime.today().time()}.xlsx', excel_buffer.getvalue(),
                     'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        print(email.send())

    def generate_excel_sheet(self, data, columns, columns_with_zero=None):
        df_output = pd.DataFrame(data, columns=columns)
        if columns_with_zero:
            df_output[columns_with_zero] = df_output[columns_with_zero].fillna(0).astype(int)
            df_output[columns_with_zero] = df_output[columns_with_zero].replace('', 0).astype(int)

        # Create BytesIO object to store Excel file in memory

        excel_file =BytesIO()
        df_output.to_excel(excel_file, index=False, engine='openpyxl')
        return excel_file