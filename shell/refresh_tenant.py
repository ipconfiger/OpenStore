#coding=utf8
__author__ = 'alex'
from nova.nova import all_tenant
from models import Tenant

def can_insert(tenant_id):
    tenant = db.query(Tenant).get(tenant_id)
    return False if tenant else True

def main():
    tenant_list = all_tenant()
    for tenant in tenant_list:
        if can_insert(tenant['id']):
            tn = Tenant(tenant['id'],tenant['name'],tenant['user_id'])
            db.add(tn)
            print "tenant :",tenant['name']," added to db"
    db.flush()
    db.commit()

