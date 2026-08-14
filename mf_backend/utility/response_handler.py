from rest_framework import status
from rest_framework.response import Response

from utility.common_utils import custom_response_obj


class ResponseSchema:

    def __init__(self, data, status_code, error_msg=None, error_code=None, count=None, next=None,
                 previous=None):
        self.data = data
        self.status_code = status_code
        self.__error_msg=error_msg
        self.__error_code=error_code
        self.__count=count
        self.__next=next
        self.__previous=previous
    def get_response(self):

        resp = custom_response_obj(message=self.data,
                                   code=self.status_code,
                                   error_msg=self.__error_msg,
                                   error_code=self.__error_code)
        if self.__count:
            resp.update(**{'count':self.__count, 'next':self.__next, 'previous':self.__previous})
        return Response(resp, status=self.status_code)


class HttpResponse:


    def __unauthorized(self, data, error_msg=None, error_code=None):
        response = ResponseSchema(data,
                                  status.HTTP_401_UNAUTHORIZED, error_msg=error_msg, error_code=error_code)
        return response.get_response()

    def __bad_request(self, data, error_msg=None, error_code=None):
        response = ResponseSchema(data,
                                  status.HTTP_400_BAD_REQUEST, error_msg=error_msg, error_code=error_code)
        return response.get_response()

    def __forbidden(self, data, error_msg=None, error_code=None):
        response = ResponseSchema(data,
                                  status.HTTP_403_FORBIDDEN, error_msg=error_msg, error_code=error_code)
        return response.get_response()

    def __internal_server_error(self, data, error_msg=None, error_code=None):
        response = ResponseSchema(data,
                                  status.HTTP_500_INTERNAL_SERVER_ERROR, error_msg=error_msg, error_code=error_code)
        return response.get_response()

    def __not_found(self, data, error_msg=None, error_code=None):
        response = ResponseSchema(data, status.HTTP_404_NOT_FOUND, error_msg=error_msg, error_code=error_code)
        return response.get_response()

    def __conflict_response(self, data, error_msg=None, error_code=None):
        response = ResponseSchema(data, status.HTTP_409_CONFLICT, error_msg=error_msg, error_code=error_code)
        return response.get_response()

    def __success_response(self, data, count=None, next=None, previous=None):
        response = ResponseSchema(data, status.HTTP_200_OK,count=count, next=next, previous=previous)
        return response.get_response()

    def __created_response(self, data):
        response = ResponseSchema(data, status.HTTP_201_CREATED)
        return response.get_response()

    def __no_content_response(self, data, count=None, next=None, previous=None):
        response = ResponseSchema(data, status.HTTP_204_NO_CONTENT,count=count, next=next, previous=previous)
        return response.get_response()

    def __delete_response(self, data):
        response = ResponseSchema(data, status.HTTP_204_NO_CONTENT)
        return response.get_response()

    def response(self, code, data, error_msg=None, error_code=None, **kwargs):
        responses = {
            200: self.__success_response(data, count=kwargs.get('count', None),
                                         next=kwargs.get('next', None),
                                         previous=kwargs.get('previous',None)),
            201: self.__created_response(data),
            204: self.__no_content_response(data),
            400: self.__bad_request(data, error_msg=error_msg, error_code=error_code),
            401: self.__unauthorized(data, error_msg=error_msg, error_code=error_code),
            403: self.__forbidden(data, error_msg=error_msg, error_code=error_code),
            404: self.__not_found(data, error_msg=error_msg, error_code=error_code),
            409: self.__conflict_response(data, error_msg=error_msg, error_code=error_code),
            500: self.__internal_server_error(data, error_msg=error_msg, error_code=error_code),
        }
        return responses.get(code)
