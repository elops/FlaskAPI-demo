#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" API server """

# author : Špoljar Hrvoje
# email  : <hrvoje.spoljar@gmail.com>

import json
import base64
import hmac
import hashlib

import mysql.connector
from mysql.connector import errorcode

from flask import Flask, request
app = Flask('harvest')  # pylint: disable=invalid-name

API_NAME = 'harvest'
API_VERSION = '0.1'
API_PREFIX = '/' + API_NAME + '/' + API_VERSION
HMAC_SECRET = '0xDEADBEEF'

DB_NAME = 'db_name'
DB_USER = 'db_user'
DB_PASS = 'db_pass'
DB_HOST = 'localhost'

## Functions ##############################################################

def add_server(server_ip, root_key, free_space):
    """ Adds server record to database """
    try:
        mysql_conn = mysql.connector.connect(user=DB_USER,
                                             password=DB_PASS, host=DB_HOST, database=DB_NAME)
        cursor = mysql_conn.cursor()
        cursor.execute("""INSERT INTO servers (server_ip, root_key, free_space)
                       VALUES (%s, %s, %s)""", (server_ip, root_key, free_space))
        cursor.close()
        mysql_conn.commit()
        mysql_conn.close()
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with your user name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        else:
            print(err)
    else:
        mysql_conn.close()

def hmac_verify(key, df_free, hmac_b64):
    """ returns boolean """
    digest = hmac.new(HMAC_SECRET.encode('utf-8'), \
                      (key + str(df_free)).encode('utf-8'), hashlib.sha1).digest()
    return hmac_b64 == base64.b64encode(digest).decode('utf-8')


## Flask routes ###########################################################

@app.errorhandler(404)
def not_found(message):
    """ 404 handler """
    return "<h1>%s</h1>" %(message), 404


@app.route(API_PREFIX, methods=['GET'])
def info():
    """ API root showing basic info """
    return """ <HEAD>
                <TITLE> %s server info API (v%s) </TITLE>
               </HEAD>
               <BODY> 
                request IP : %s 
               </BODY>
           """ %(API_NAME, API_VERSION, request.remote_addr)


@app.route(API_PREFIX + '/add', methods=['POST'])
def add_one():
    """ API route to read and parse request and relay data to be stored """
    if request.json:
        data = json.loads(request.json)
        hmac_b64 = data.get("hmac")
        key = data.get("key")
        df_free = data.get("df_free")

        if hmac_verify(key, df_free, hmac_b64):
            add_server(request.remote_addr, key, df_free)
            return "{ 'ok' : %s }" %(hmac_b64)
        else:
            print('HMAC check failed!')
    else:
        return "No JSON data found!"

## Main ###################################################################

if __name__ == '__main__':
    CONTEXT = ('ssl/certificate.crt', 'ssl/private.key')
    app.run(debug=True, host='0.0.0.0', ssl_context=CONTEXT, port=8080)
