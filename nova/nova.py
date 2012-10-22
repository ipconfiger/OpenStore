#coding=utf8
__author__ = 'alex'
import api
import time

ADMIN_TENANT = ('admin','aipuip662012','adminTenant')

def gen_key(tenant_id):
    name = str(int(time.time()))
    token = api.Token(*ADMIN_TENANT)
    tenant = api.Tennat(token,tenant_id=tenant_id)
    return tenant.gen_key(name)


