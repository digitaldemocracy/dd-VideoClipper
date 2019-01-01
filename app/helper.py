import os
import requests 
import hashlib
from datetime import datetime
from flask import request

def create_outfile(salt, videofiles=None, ext='.mp4'):
	m = hashlib.md5()
	strtime = datetime.now().strftime("%Y%m%d%H%M%S%f")
	m.update(salt)
	m.update(strtime)
	for videofile in videofiles:
		m.update(videofile)
	root = os.path.splitext(videofiles[0])
    #ext = root[-1]
	return m.hexdigest() + ext 

def get_env_var(variable_name):
    variable = os.environ.get(variable_name)
    if variable is None:
        variable = request.environ.get(variable_name)
    return variable

def validate_client(client_ip):
    print client_ip
    allowed_ip = {"54.149.231.2":1, "54.149.111.236":1,\
            "54.68.146.239":1, "54.201.84.228":1, "127.0.0.1":1,\
            "129.65.22.190":1, "129.65.248.13":1, "66.214.65.115":1,\
            "52.41.153.148":1, "127.0.0.1":1}
    if client_ip in allowed_ip and allowed_ip[client_ip] == 1:
        return True
    return False
