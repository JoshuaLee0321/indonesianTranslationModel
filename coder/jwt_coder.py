import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import configparser
from jose import jwt
from Crypto.Hash import SHA
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5 as Signature_pkcs1_v1_5
from jose.exceptions import *
config = configparser.ConfigParser()
import time
config.read(os.path.dirname(os.path.abspath(__file__))+"/setting_token.ini",encoding="utf-8")
#print(os.path.dirname(os.path.abspath(__file__))+"/setting_token.ini")


class jwtDecoder:
    def __init__(self,token):
        self.valid = True
        self.excpt = None
        self.token = token
        self.payload = ""
        self.decode()
    def decode(self):
        rsapubKey = open(os.path.dirname(os.path.abspath(__file__))+'/rsa_public_key_token_test.pem').read()
        try:
            self.payload = jwt.decode(self.token,rsapubKey,audience=config.get("payload","aud"))
        except JWTError as e:
            self.valid = False
            self.excpt = str(type(e))
            print(type(e))
        except JWTClaimsError as e:
            self.valid = False
            self.excpt = str(type(e))
            print(type(e))
        except ExpiredSignatureError as e:
            self.valid = False
            self.excpt = str(type(e))
            print(type(e))

class jwtEncoder:
    def __init__(self,payload):
        rsapriKey = open(os.path.dirname(os.path.abspath(__file__))+'/rsa_private_key_token_test.pem').read()
        self.token = jwt.encode(payload, key=rsapriKey, algorithm="RS512")

def payloadFormat(id,user_id,service_id,scopes,sub="",iat=int(time.time()),exp=int(time.time())+60*60*24*365,nbf=int(time.time())):
    payload = {
            "id":id,# 必
            "user_id":user_id,# 必
            "service_id":service_id,# 必
            "scopes":scopes,# 必
            "sub":sub,
            "iat":iat,
            "nbf":nbf,
            "exp":exp,
            "iss":config.get("payload","iss"),
            "aud":config.get("payload","aud"),
            "ver":0.1
    }
    return payload


if __name__ == "__main__":
    key = config.get("important","key")
    #j = jwtEncoder(payloadFormat(0,"888",1,2,"lorne"))
    import time
    start_time_0 = time.time()
    #s = jwtDecoder(j.token)
    start_time_1 = time.time()
    #print(start_time_1 - start_time_0)
    #print(j.token)
    #print(jwtDecoder(j.token).valid)
    #print(s.valid)
    token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzUxMiJ9.eyJhdWQiOiJ3bW1rcy5jc2llLmVkdS50dyIsInNjb3BlcyI6IjEiLCJpc3MiOiJKV1QiLCJzZXJ2aWNlX2lkIjoiMyIsInZlciI6MC4xLCJleHAiOjE1NDA0MzkyODMsImlkIjo2OCwic3ViIjoiIiwibmJmIjoxNTQwNDM4OTgzLCJpYXQiOjE1NDA0Mzg5ODMsInVzZXJfaWQiOiIyMiJ9.oL3ZdTpJhaNP6KSXIIoNNyVsn-vpAmAR1Fi76zoz42agBtfnh8qqRvmTrLxbT5HyDkIwnpZOabhbVVGBrOfZEMQVY7HSbg4Anr3DEaxsj0FtSvB29UPS15AjUZG2gyTWpf-tG-xK2jgXc-42pCAsOFioKNwIXiNh0eb6HCrcy8w"
	
	

    j = (jwtDecoder(token))
    print(j)
    print(jwtDecoder(token).payload)
    #unix_ts = jwtDecoder(token).payload['exp']
    #from datetime import datetime, timedelta
    #print((datetime.fromtimestamp(unix_ts) - timedelta(hours=2)).strftime('%Y-%m-%d %H:%M:%S'))
    #unix_ts = jwtDecoder(token).payload['iat']
    #from datetime import datetime, timedelta
    #print((datetime.fromtimestamp(unix_ts) - timedelta(hours=2)).strftime('%Y-%m-%d %H:%M:%S'))

    # import testdata
    # print(testdata.payload)
    # print(jwtEncoder(testdata.payload))
    # print(jwtDecoder(jwtEncoder(testdata.payload).token).valid)
    # print(testdata.testdata1)
    # print(jwtEncoder(testdata.testdata1))
    # print(jwtDecoder(jwtEncoder(testdata.testdata1).token).valid)
    # print(testdata.testdata2)
    # print(jwtEncoder(testdata.testdata2))
    # print(jwtDecoder(jwtEncoder(testdata.testdata2).token).valid)
    # print(testdata.testdata3)
    # print(jwtEncoder(testdata.testdata3))
    # print(jwtDecoder(jwtEncoder(testdata.testdata3).token).valid)
