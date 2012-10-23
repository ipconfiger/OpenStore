#coding=utf8
__author__ = 'alex'
import api
import time
import settings

def auth():
    return api.Token(*settings.NOVA_ADMIN)

def all_tenant():
    results = []
    token = auth()
    tenant_access = api.Tenant(token)
    tenants = tenant_access.tenant_list()
    for tenant in tenants["tenants"]:
        tenant_access(tenant["id"])
        users = tenant_access.user_list()
        print "tenant:", tenant["name"]
        print users


def all_key():
    token = auth()
    sec = api.Security(token)
    return sec.list_key()

def gen_key():
    name = str(int(time.time()))
    token = auth()
    sec = api.Security(token)
    return sec.gen_key(name)

def get_tenent():
    return ""

