#coding=utf8
__author__ = 'alex'
import api
import time
import settings
from models import Tenant
from flask import g
import logging as log
import  utils

def auth(tenant_name=None, admin=None, password=None):
    if not tenant_name:
        return api.Token(*settings.NOVA_ADMIN)
    else:
        return api.Token(admin, password, tenant_name)

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

def get_tenent(useraccount):
    tenant = g.db.query(Tenant).filter(Tenant.used==False).first()
    tenant.used = True
    token = auth()
    useraccount.tenant_password = "".join(utils.read_random(10))
    useraccount.tenant_password = useraccount.tenant_password.lower()
    name = useraccount.user.login_name.replace("@","").replace(".","")
    ua = api.User(token,None)
    user_id = ua.create(name, useraccount.tenant_password, useraccount.user.login_name, enabled=True)
    role = api.Role(token).get_role_id("projectmanager")
    rep = api.Tenant(token,tenant_id=tenant.id).append_user(user_id, role)
    g.db.flush()
    g.db.commit()
    return dict(id=tenant.id,name=tenant.name,user_id=tenant.admin_user_id)


def get_images():
    token = auth()
    platform = api.Platform(token)
    return [dict(id=image['id'],name=image["name"]) for image in platform.image_list()["images"]]


def create_server(useraccount,tenant_name, server_name, favor_id, image_id, secure, key_name):
    token = auth(tenant_name=tenant_name,admin=useraccount.user.login_name.replace("@","").replace(".",""),password=useraccount.tenant_password)
    server_acc = api.Server(token)
    server_data = server_acc.create(server_name,image_id,favor_id,secure,key_name)
    log.error(server_data)
    server = api.ServerInstance(server_data)
    return True, server.id, server.password

def get_vnc_url(tenant_name, server_id):
    token = auth(tenant_name=tenant_name)
    server_acc = api.Server(token,server_id=server_id)
    results = server_acc.openvnc()
    return results["console"]["url"]


def server_status(server_id):
    token = auth()
    server_access = api.Server(token,server_id=server_id)
    detail = server_access.detail()
    return api.ServerInstance(detail)
