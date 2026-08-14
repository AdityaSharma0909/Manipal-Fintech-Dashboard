from utils.envSetup import environment
import jwt

class CreateJWTToken:

    def create_token(self, payload):
        secret=environment.SPRINT_SECRET
        access_token=jwt.encode(payload, secret, algorithm='HS256')
        return access_token

