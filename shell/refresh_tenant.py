#coding=utf8
__author__ = 'alex'
from nova.nova import *
from models import Tenant

def can_insert(tenant_id):
    return False if db.query(Tenant).get(tenant_id) else True

def main():
    tenant_list = get_tenent()["tenants"]
    for tenant in tenant_list:
        if tenant["enabled"] and tenant["name"] not in ["aipuTenent","adminTenant","serviceTenant","maotaiTenant"]:

            print tenant["id"],tenant["name"]

