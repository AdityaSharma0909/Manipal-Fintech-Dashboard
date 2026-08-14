from utils.responseHandler import HttpResponse
def custom_response_obj(message,code):
        resp_status='success' if code==200 or code==201 or code==204 else 'error'
        if resp_status=='success':
            return HttpResponse.Success({'status': resp_status, 'response': message, 'code': code})
        else:
            return HttpResponse.BadRequest({'status': resp_status, 'response': message})


class SerilizerInstance:

    

    def serializer_instance(self, serializer_instance,data):
        serializer=serializer_instance(data=data)
        if serializer.is_valid():
            serializer.save()
            return custom_response_obj(message=serializer.data, code=200)
        error={k: ','.join([str(j) for j in v]) for k, v in serializer.errors.items()}
        return custom_response_obj(message=error, code=400)
    