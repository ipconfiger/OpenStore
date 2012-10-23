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
        if tenant["enabled"] and tenant["name"] not in ["aipuTenent","adminTenant","serviceTenant","maotaiTenant"]:
            tenant_access(tenant["id"])
            users = tenant_access.user_list()
            user_items = users["users"]
            user = None
            if not user_items:
                continue
            for u in user_items:
                if u["tenantId"]:
                    user = u
                    break
            if not user:
                continue
            results.append(dict(
                id = tenant["id"],
                name = tenant["name"],
                user_id = user["id"],
            ))
    return results


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

