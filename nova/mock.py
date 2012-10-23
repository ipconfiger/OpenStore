#coding=utf8
from uuid import uuid4
__author__ = 'alex'

def get_tenent():
    return uuid4().hex

def regist_key():
    return ""

def get_image_list():
    return []

def create_server(server_name, favor_id, image_id, secure, key_name):
    return True, uuid4().hex

def server_status(server_id):
    return "working"