class LoanGLPL:


    def process(self, application):
        try:
            error_msg=None
            is_product_eligible=self.__validate_product(product=application.product)
            if is_product_eligible:
                is_application_eligible=self.__validate_application(application)
                if is_application_eligible:
                    return True, 'application_eligible'
                else:
                    error_msg='application not eligible for contra loan'
            else:
                error_msg='product not eligible for contra loan'
            return False,error_msg
        except Exception as e:
            return False,str(e)


    def __validate_product(self, product):
        return product.contra_product is not None


    def __validate_application(self, application):
        return application.contra_loan_amount is not None



