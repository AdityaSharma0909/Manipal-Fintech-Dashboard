import datetime
from utils.constants import CODE_OF_STATES,NO_OF_LOCATION,TYPE_OF_LOCATION
import utils.helper as helper

class LoanService:
    def generate_loan_number(self):

        location=TYPE_OF_LOCATION.BRANCHES.value+CODE_OF_STATES.MAHARASTRA.value+NO_OF_LOCATION.REGISTERED_OFFICE_GURGAON.value
        
        

        
        
        number=helper.generate_numbers(6)
    

        return location+"SLHM"+number