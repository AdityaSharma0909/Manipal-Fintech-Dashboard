import traceback
from abc import abstractmethod

from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status
import logging
from utility.common_utils import normalize_serializer_error
from utility.error_handler import HttpErrors
from utility.response_handler import HttpResponse

logger = logging.getLogger('radian')

"""
    This class can be used as an abstract class for all the APIViews which have common flow of
    serializer check and try/except block. It helps improve readability and maintaining the code
    code flow:it contains of main method with format_request, run_logic, process
    
            1. first format request is called
            2. then run_logic is called
            3. then process return final result to main method
"""


class ApiFramework:

    def __init__(self, serializer_class=None):
        self.serializer = serializer_class

    def main(self):
        """
            this is the main method of this class, it returns the final result as instance of Response class
            with help of custom Http response class.
        """
        response = ''
        try:
            if self.serializer is None or self.serializer.is_valid():
                self.format_request()
                self.run_logic()
                data = self.process()
                status_code = data.get('status_code',200)
                message=data.get('data')
                response = HttpResponse().response(code=status_code, data=message,error_code=data.get('error_code', None),
                                                   error_msg=data.get('error_msg'),
                                                   count=data.get('count', None),
                                                   next=data.get('next', None),
                                                   previous=data.get('previous', None))
            else:
                serializer_error = normalize_serializer_error(self.serializer.errors.items())
                response = HttpResponse().response(code=400, data=serializer_error, error_code=400, error_msg=serializer_error)

        except ObjectDoesNotExist:
            response=HttpResponse().response(code=404, data={'msg':"data not found"}, error_msg={'msg':"data not found"},
                                             error_code=404)
        except Exception as e:
            traceback.print_exc()
            logger.exception('Exception ' + str(e))
            response = HttpErrors.InternalServerError(str(e))

        return response

    @abstractmethod
    def format_request(self):
        """
            custom request formatting if required
        """
        pass

    @abstractmethod
    def run_logic(self):
        """
            custom logic of the API
        """
        pass

    @abstractmethod
    def process(self):
        """
            must return the response to the main methodI
        """
        pass
