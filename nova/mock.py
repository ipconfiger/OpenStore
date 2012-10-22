#coding=utf8
from uuid import uuid4
__author__ = 'alex'

def get_tenent():
    return uuid4().hex

def regist_key():
    return ""

def get_image_list():
    return []

def create_server(tenant_id, favor_id, image_id):
    return True, uuid4().hex

def server_status(tenant_id , server_id):
    return "working"