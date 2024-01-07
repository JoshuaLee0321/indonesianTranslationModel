# -*- coding: utf-8 -*-
"""
Created on Thu Apr 12 09:03:58 2018

@author: lorne
this is a testing file
include 4 token,use jwt_coder.encoder to use it.
1-2 is alaways correct
3-4 is alaways incorrect because different reasons
"""
import configparser
import os
config = configparser.ConfigParser();
config.read(os.path.dirname(os.path.abspath(__file__))+"/setting_token.ini")

#alaways pass
payload = {
            "iss":config.get("payload","iss"),#issuer
            "aud":config.get("payload","aud"),#audience *important
            "service":"Ner",
            "username":"wu",
            "scopes":"admin",
            "sub":"2019",#subject rules
            "iat":1532085696,#sign time
            "exp":2632085696,#expiration time
            "nbf":1532085696#(Not Before) Claim
        }
# more detail https://tools.ietf.org/html/rfc7519#section-4.1
#alaways pass
testdata1 = {
            "iss":config.get("payload","iss"),
            "aud":config.get("payload","aud"),
            "service":"Ner",
            "username":"wu",
            "scopes":"admin",
            "sub":"2019",
            "iat":1532085696,
            "exp":2563621696,
            "nbf":1523495215
        }
#not ready
testdata2 = {

            "iss":config.get("payload","iss"),
            "aud":config.get("payload","aud"),
            "service":"Ner",
            "username":"wu",
            "scopes":"admin",
            "sub":"2019",
            "iat":1563621696,
            "exp":1564621696,
            "nbf":1563621696#late
        }
#already expired
testdata3 = {

            "iss":config.get("payload","iss"),
            "aud":config.get("payload","aud"),
            "service":"Ner",
            "username":"wu",
            "scopes":"admin",
            "sub":"2019",
            "iat":1523495213,
            "exp":1523495213,#late
            "nbf":1523495213
        }
