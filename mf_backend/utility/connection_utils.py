import requests


class ConnectionUtil:

    def process_request(self, method, url, headers, **kwargs):
        response = requests.request(method, url, headers=headers, **kwargs)
        return response.json()
