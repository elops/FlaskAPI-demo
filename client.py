#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" API client """

# author : Špoljar Hrvoje
# email  : <hrvoje.spoljar@gmail.com>

import json
import sys
import os
import base64
import hmac
import hashlib
import requests

# sole purpose to disable ssl warnings
import urllib3
urllib3.disable_warnings()

## Settings
API_NAME = 'harvest'
API_VERSION = '0.1'
API_PREFIX = '/' + API_NAME + '/' + API_VERSION

API_URL = 'https://localhost:8080' + API_PREFIX + '/add'
KEY_PATH = os.environ['HOME'] + '/.ssh/id_rsa.pub'
HMAC_SECRET = '0xDEADBEEF'

STATVFS = os.statvfs('/')
DF_FREE = str(STATVFS.f_frsize * STATVFS.f_bfree / (1024 * 1024))

if __name__ == '__main__':
    try:
        with open(KEY_PATH, 'r') as f:
            KEY = f.read().rstrip('\n')
    except IOError as err:
        print("I/O error{0}".format(err))
        exit(1)
    except:
        print("Unexpected error:", sys.exc_info()[0])
        exit(1)

    DATA = {}
    DATA['key'] = KEY
    DATA['df_free'] = DF_FREE

    DIGEST = hmac.new(HMAC_SECRET.encode('utf-8'), \
                    (KEY + DF_FREE).encode('utf-8'), hashlib.sha1).digest()
    DATA['hmac'] = base64.b64encode(DIGEST).decode('utf-8')

    JSON_DATA = json.dumps(DATA)

    try:
        # didn't make valid cert so had to disable checks // verify=False
        RESPONSE = requests.post(API_URL, json=JSON_DATA, verify=False)
        print(RESPONSE.content.decode('utf-8'))
    except requests.exceptions.ConnectionError:
        print("Could not connect to %s" %(API_URL))
