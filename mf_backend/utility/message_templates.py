class MessageTemplates:

    def message_template(self, template, application, customer_name):
        templates={
            'application_submitted':f"Your loan application has been initiated (Application No.{application} and Customer Name: {customer_name}). And our staff is presently working on the request. We'll keep you updated on progress. Radian Loans",
            'application_roll_back':f"The CPC team has rolled back your application (Application No.{application} and Customer Name: {customer_name}). Please refer to the app for additional details. Radian Finserv Loans",
            'application_rejected':f"We regret to notify you that your loan application (Application No.{application} and Customer Name: {customer_name}) has been rejected. Please refer to the app for further information. Radian Finserv Loans",
            'application_approved':f"Your loan application (Application No.{application} and Customer Name: {customer_name}) has been approved and will be disbursed shortly. Radian Finserv Loans",
            'application_disbursed':f"We are pleased to alert you that your loan application (Application No.{application} and Customer Name: {customer_name}) has been approved. An amount has been credited to the customer account. Radian Finserv Loans"
        }
        return templates[template]
