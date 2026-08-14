from loan.models import LoanEMIRecord, Loan, DemandGeneration
from utility.crud_helper import CrudHelper


class LoanPaymentService(CrudHelper):
    def __init__(self, serializer, data):
        super().__init__(serializer)
        self.__serializer=serializer
        self.__data=data

    def add_loan_data(self):
        self.loan_payment_division()
        response=self.add_obj(data=self.__data,validate_add=True,validate_model=Loan, value=self.__data.get('loan_id'))
        return response
    def loan_payment_division(self):
        loan_id=self.__data.get('loan_id')
        repayment_data=self.__get_loan_repayment_schedule(loan_id)
        payment_done_by_customer=self.__data.get('payment_amount')
        print('data',repayment_data)
        for i in repayment_data:
            #reduce penalty first
            print(payment_done_by_customer,i.penalty_remaining)
            can_deduct_more,payment_done_by_customer=self.__reduce_amount(repayment_amount=payment_done_by_customer,
                                                          pending_payment=i.penalty_remaining)
            penalty=0 if can_deduct_more==1 else payment_done_by_customer
            interest=i.emi_record.interest
            if can_deduct_more==1:
                #reduce interest
                can_deduct_more,payment_done_by_customer=self.__reduce_amount(repayment_amount=payment_done_by_customer,
                                                                              pending_payment=i.emi_record.interest)
                interest=0 if can_deduct_more==1 else payment_done_by_customer

            principal=payment_done_by_customer
            #reduce principal
            if can_deduct_more==1:
                can_deduct_more,payment_done_by_customer=self.__reduce_amount(
                                                            repayment_amount=payment_done_by_customer,
                                                            pending_payment=i.emi_record.principal)
                principal=0 if can_deduct_more==1 else payment_done_by_customer

            self.settle_payment_mark_paid(bill_instance=i, emi_record=i.emi_record,penalty=penalty, interest=interest,
                                          principal=principal)
            print('can deduct more', principal, interest, penalty, payment_done_by_customer)
            if (principal==0 and interest==0 and penalty==0 and payment_done_by_customer==0) or can_deduct_more==0:
                break
    def settle_payment_mark_paid(self, bill_instance, emi_record, interest=0, principal=0, penalty=0):
        bill_settled=interest==0 and penalty==0 and principal==0
        emi_record.paid=bill_settled
        emi_record.save()
        bill_instance.principal_remaining=principal
        bill_instance.interest_remaining=interest
        bill_instance.penalty_remaining=penalty
        bill_instance.bill_paid=bill_settled
        bill_instance.save()


    def __reduce_amount(self, repayment_amount, pending_payment):
        """
            here we deduct amount from the amount customer paid, we return
            0: if after deduction the amount paid by customer is zero and cannot be further deducted
            1: if after deduction the amount is not zero and can be further deducted
            2: this is the case where customer has paid less than the actual emi, if emi is 100 where penalty is 10,
            interest is 50 and principal is 40 and customer only makes 40 as payment in this case we can only deduct
            penalty and part of interest which is 40 and still interest and principal would be remaining
        """
        print(repayment_amount, pending_payment)
        if repayment_amount==0:
            return 0, pending_payment
        if repayment_amount>pending_payment:
            print(repayment_amount-pending_payment)
            repayment_amount-=pending_payment
            return 1, repayment_amount
        else:
            pending_payment-=repayment_amount
            return 2, pending_payment


    def __get_loan_repayment_schedule(self, loan_id):
        loan_repayment=DemandGeneration.objects.filter(loan__loan_id=loan_id, bill_paid=False).order_by('emi_record__sequence_no')
        return loan_repayment


    def __get_loan_instance(self, loan_id):
        return Loan.objects.get(loan_id=loan_id)