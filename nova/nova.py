#coding=utf8
__author__ = 'alex'
import api
import time

ADMIN_TENANT = ('admin','aipuip662012','adminTenant')


def all_tenant():
    token = api.Token(*ADMIN_TENANT)
    tenant = api.Tenant(token)
    return tenant.tenant_list()

def all_key():
    token = api.Token(*ADMIN_TENANT)
    sec = api.Security(token)
    return sec.list_key()

def gen_key():
    name = str(int(time.time()))
    token = api.Token(*ADMIN_TENANT)
    sec = api.Security(token)
    return sec.gen_key(name)


