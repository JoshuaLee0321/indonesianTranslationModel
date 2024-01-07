# -*- coding: utf-8 -*-
"""
Created on Mon Apr  9 12:12:16 2018

@author: lorne
this file can handle encode and decode
just use class
"""

import configparser
from jose import jwt
from jose.exceptions import *
import time
config = configparser.ConfigParser()
config.read("setting_token.ini",encoding="utf-8")

# for jwt decoder
class jwtDecoder:
    def __init__(self,token):
        self.valid = True
        self.excpt = None
        self.token = token
        self.decode()
    def decode(self):
        try:
            self.payload = jwt.decode(self.token,config.get("important","key"),audience=config.get("payload","aud"))
        except JWTError as e:
            self.valid = False
            self.excpt = str(type(e))
            #print(type(e))
        except JWTClaimsError as e:
            self.valid = False
            self.excpt = str(type(e))
            #print(type(e))
        except ExpiredSignatureError as e:
            self.valid = False
            self.excpt = str(type(e))
            #print(type(e))

# for jwt encoder
class jwtEncoder:
    def __init__(self,payload):
        self.token = jwt.encode(payload, key=config.get("important","key"), algorithm="HS512")

# generate payload for jwtEncoder
def payloadFormat(service,scopes,sub,username,iat=int(time.time()),exp=int(time.time())+60*60*24*365*2,nbf=int(time.time())):
    payload = {
            "iss":config.get("payload","iss"),
            "aud":config.get("payload","aud"),
            "service":service,
            "username":username,
            "scopes":scopes,
            "sub":sub,
            "iat":iat,
            "exp":exp,
            "nbf":nbf
    }
    return payload

if __name__ == "__main__":
    key = config.get("important","key")
    j = jwtEncoder(payloadFormat("888","1","2","lorne"))
    s = jwtDecoder(j.token)
    print(s.valid)
    print(s.token)
    print(j.token)
