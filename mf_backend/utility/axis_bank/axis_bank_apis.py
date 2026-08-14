import requests

class AxisBankApi:

    def __create_request_data(self,):
        return {"request": {
                    "header": {"subHeader": {
                    "requestUUID": "12345",
                    "serviceRequestId": "AE.ESB.CRMNXT.SSTP.001",
                    "serviceRequestVersion": "1.0",
                    "channelId": "ESB"
                    }
                    },
        }
        }
    def login(self, data):
        url='https://esbuat2.axisb.com/crmnext/createandupdateleaddetails/enc/login'


    def __process_request(self, method, url, **kwargs):
        #headers = self.__process_headers()
        if method == 'GET':
            response = requests.request('GET', url, **kwargs)
        else:
            response = requests.request(method, url, **kwargs)
        return response.json()
