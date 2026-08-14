from rest_framework import status
from rest_framework.response import Response


class ErrorSchema():
    def __init__(self, errorMsg, errorCode, statusCode, data=None):
        self.errorMsg = errorMsg
        self.errorCode = errorCode
        self.statusCode = statusCode
        self.data=data

    def getErrorResponse(self):
        return Response({
            'status': 'error',
            'data':self.data,
            'error_msg': self.errorMsg,
            'error_code': self.errorCode,
        }, status=self.statusCode)

class SuccessSchema():
    def __init__(self, data, statusCode):
        self.data = data
        self.statusCode = statusCode

    def getSuccessResponse(self):

        return Response({
            'status': 'success',
            'data': self.data,
        }, status=self.statusCode)


class HttpResponse():
    # def customResponse(errorMsg, errorCode):
    #     err = ErrorSchema(errorMsg, errorCode)
    #     return err.getErrorResponse()
    
    @staticmethod
    def NotFound(errorMsg, data=None, errorCode='HTTP_404_NOT_FOUND'):
        err = ErrorSchema(errorMsg, errorCode, status.HTTP_404_NOT_FOUND, data=data)
        return err.getErrorResponse()

    def Success(data):
        resp = SuccessSchema(data, status.HTTP_200_OK)
        return resp.getSuccessResponse()

    def NoContent(data):
        resp = SuccessSchema(data, status.HTTP_204_NO_CONTENT)
        return resp.getSuccessResponse()

    def Unauthorized(errorMsg, errorCode='HTTP_401_UNAUTHORIZED'):
        err = ErrorSchema(errorMsg, errorCode, status.HTTP_401_UNAUTHORIZED)
        return err.getErrorResponse()

    def Forbidden(errorMsg, errorCode='HTTP_403_FORBIDDEN'):
        err = ErrorSchema(errorMsg, errorCode, status.HTTP_403_FORBIDDEN)
        return err.getErrorResponse()

    def BadRequest(errorMsg, data=None,errorCode='HTTP_400_BAD_REQUEST'):
        err = ErrorSchema(errorMsg, errorCode, status.HTTP_400_BAD_REQUEST, data=data)
        return err.getErrorResponse()

    def InternalServerError(errorMsg, errorCode='HTTP_500_INTERNAL_SERVER_ERROR'):
        err = ErrorSchema(errorMsg, errorCode, status.HTTP_500_INTERNAL_SERVER_ERROR)
        return err.getErrorResponse()

    def Accepted(data):
        resp = SuccessSchema(data, status.HTTP_202_ACCEPTED)
        return resp.getSuccessResponse()
