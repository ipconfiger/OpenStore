#coding=utf8
__author__ = 'alex'

import requests
import base64
import json
import logging as log

KEYSTORN_READ = "http://10.1.1.4:5000"
KETSTORN_WRITE = "http://10.1.1.4:35357"


COMMON_HEADER = {"Content-type":"application/json"}
PERSONAL_PATH = "/etc/banner.txt"

def header(token):
    return {"X-Auth-Token":token.id, "Content-type":"application/json" }

def fetch(url, data, headers, method):
    try:
        if data==None:
            r=method(url,headers=headers)
        else:
            r=method(url,data=json.dumps(data),headers=headers)
        if r.status_code in [200,201,202,203]:
            return r.json
        log.error("\n-----------------error---------------\naccess %s with error code %s\n%s"%(url,r.status_code,r.text))
    except Exception,e:
        log.error(e.message)


def get_token(osuser, ospassword, ostenant):
    """
    登陆keystone获取登陆token
    :param osuser: 用户名
    :param ospassword:密码
    :param ostenant: 租户
    :return:返回登陆token
    """
    url="%s/v2.0/tokens"%KEYSTORN_READ
    body={"auth":{"passwordCredentials": {"username": osuser, "password": ospassword}, "tenantName":ostenant}}
    result = fetch(url, body, COMMON_HEADER, requests.post)
    if result:
        return result

class Token(object):
    """
    抽象token概念的类，用于解析token内容
    """
    def __init__(self, osuser, ospassword, ostenant):
        self.token=get_token(osuser, ospassword, ostenant)
        self.valid=True if self.token else False
        self.id=self.token['access']['token']['id']

    def __getitem__(self, item):
        for catalog in self.token['access']['serviceCatalog']:
            if catalog['name']==item:
                return catalog['endpoints'][0]['adminURL']
        return ""

    def get_tenant(self):
        return self['nova'].split('/')[-1]

class Nova(object):
    """
    访问Nova的API
    """
    def nova_process(self, path, body, method):
        url = self.token['nova'] + path
        return fetch(url, body, header(self.token), method)


class KeyStornRead(object):
    """
    访问KeyStorn只读
    """
    def kr_process(self, path, body, method):
        url = KEYSTORN_READ + path
        return fetch(url, body, header(self.token), method)

class KeyStornWrite(object):
    """
    访问KeyStorn操作
    """
    def kw_process(self, path, body, method):
        url = KETSTORN_WRITE + path
        return fetch(url, body, header(self.token), method)

class Role(KeyStornWrite):
    def __init__(self, token):
        self.token = token

    def role_list(self):
        """
        获取所有role列表
        :return:
        """
        return self.kw_process("/v2.0/OS-KSADM/roles",None,requests.get)

    def get_role_id(self,name):
        roles=self.role_list()
        for r in roles["roles"]:
            if r['name']==name:
                return r["id"]

class User(KeyStornRead,KeyStornWrite):
    """
    操作用户对象
    """
    def __init__(self, token, user_id):
        self.token = token
        self.user_id = user_id

    def create(self, username, password, email, enabled=True):
        """
        """
        if self.user_id:
            return
        path = "/v2.0/users"
        body = {"user": {"name": username,
                             "password": password,
                             "email": email,
                             "enabled": enabled}}
        return self.kw_process(path,body,requests.post)

    def delete(self):
        """
        删除用户
        :return:
        """
        if self.user_id:
            path = "/v2.0/users/%s"%self.user_id
            return self.kw_process(path,None,requests.delete)

    def update_email(self, new_email):
        """
        更新用户的email
        :param new_email:
        :return:
        """
        if self.user_id:
            path = "/v2.0/users/%s"%self.user_id
            restbody = {'user':{'id':self.user_id},'email':new_email}
            return self.kw_process(path,restbody,requests.post)

    def update_password(self, new_password):
        """
        更新用户的密码
        :param new_password:
        :return:
        """
        if self.user_id:
            path = "/v2.0/users/%s"%self.user_id
            restbody = {'user':{'id':self.user_id},'password':new_password}
            return self.kw_process(path,restbody,requests.post)

    def get_user_role_id(self):
        """
        获取用户的roleid
        :return:
        """
        result = self.get_user_role_refs()
        if result:
            return result['roles'][0]['roleId']

    def get_user_role_refs(self):
        """
        获取用户的role对象
        :return:
        """
        if self.user_id:
            path="/v2.0/users/%s/roleRefs"%self.user_id
            return self.kw_process(path,None,requests.get)

    def all_user_list(self):
        """
        获取所有用户
        :return:
        """
        return self.kr_process("/v2.0/users",None,requests.get)


class Tenant(KeyStornRead,KeyStornWrite):
    """
    租户操作API
    """
    def __init__(self, token, tenant_id = None):
        self.token = token
        self.tenant_id = tenant_id

    def __call__(self, tenant_id):
        """
        附加租户ID
        :param tenant_id:
        :return:
        """
        self.tenant_id = tenant_id

    def create(self, tenant_name, description, enabled=True):
        """
        创建租户
        :param tenant_name:租户名称
        :param description:租户描述
        :param enabled:是否生效
        :return:
        """
        if self.tenant_id:
            return
        path = "/v2.0/tenants"
        restbody = {"tenant": {
            "name": tenant_name,
            "description": description,
            "enabled": enabled}}
        return self.kw_process(path,restbody,requests.put)

    def update(self,tenant_name, description, enabled=True):
        """
        更新租户信息
        :param tenant_name:租户名称
        :param description:租户描述
        :param enabled:是否生效
        :return:
        """
        if not self.tenant_id:
            return
        path = "/v2.0/tenants/%s"%self.tenant_id
        restbody = {"tenant": {'id': self.tenant_id}}
        if description:
            restbody['tenant']['description'] = description
        if enabled != None:
            restbody['tenant']['enabled'] = enabled
        return self.kw_process(path, restbody, requests.post)

    def delete(self):
        """
        删除租户
        :return:
        """
        if not self.tenant_id:
            return
        path = "/v2.0/tenants/%s"%self.tenant_id
        return self.kw_process(path, None, requests.delete)

    def append_user(self, user_id, role_id):
        """
        附加用户到租户
        :param user_id:用户ID
        :param role_id: 用户组ID
        :return:
        """
        path = "/v2.0/tenants/%s/users/%s/roles/OS-KSADM/%s"%(self.tenant_id, user_id, role_id)
        return self.kr_process(path,None,requests.put)

    def remove_user(self, user_id, role_id):
        """
        从租户移除用户
        :param user_id:用户ID
        :param role_id:用户组ID
        :return:
        """
        path = "/v2.0/tenants/%s/users/%s/roles/OS-KSADM/%s"%(self.tenant_id, user_id, role_id)
        return self.kr_process(path,None,requests.delete)

    def user_list(self):
        """
        获取租户下用户列表
        :return:
        """
        path="/v2.0/tenants/%s/users"%self.tenant_id
        return self.kr_process(path,None,requests.get)

    def tenant_list(self):
        """
        获取所有租户列表
        :return:
        """
        return self.kr_process("/v2.0/tenants",None,requests.get)



class Security(Nova):
    def __init__(self, token, security_id=None):
        self.security_id = security_id
        self.token = token

    def all(self):
        """
        获取安全组列表
        """
        return self.nova_process("/os-security-groups",None,requests.get)

    def add(self, name, description):
        """
        添加安全组
        """
        path="/os-security-groups"
        body={
            "security_group": {
                "name": name,
                "description": description
            }
        }
        return self.nova_process(path,body,requests.post)

    def get(self):
        """
        获取安全组信息
        """
        path="/os-security-groups/%s"%self.security_id
        return self.nova_process(path,None,requests.get)

    def delete(self):
        """
        删除安全组
        """
        path="/os-security-groups/%s"%self.security_id
        return self.nova_process(path,None,requests.delete)

    def add_rule(self, ip_protocol, from_port, to_port, parent_group_id, cidr):
        """
        添加安全规则
        """
        path="/os-security-group-rules"
        body={
            "security_group_rule": {
                "ip_protocol": ip_protocol,
                "from_port": from_port,
                "to_port": to_port,
                "cidr": cidr,
                "group_id": self.security_id,
                "parent_group_id": parent_group_id
            }
        }
        return self.nova_process(path,body,requests.post)

    def list_rule(self,rule_id):
        path="/os-security-group-rules/%s"%rule_id
        return self.nova_process(path,None,requests.post)

    def list_key(self):
        path = "/os-keypairs"
        return self.nova_process(path, None, requests.get)

    def gen_key(self, key_name):
        path = "/os-keypairs"
        data = {"keypair": {
            "name": key_name,
            }
        }
        return self.nova_process(path,data,requests.post)

    def get_key(self,key_name):
        path = "/os-keypairs/%s"%key_name
        return self.nova_process(path, None, requests.get)

    def rm_key(self, key_name):
        path = "/os-keypairs/%s"%key_name
        return self.nova_process(path, None, requests.delete)



class Platform(Nova):
    """
    平台级别API
    """
    def __init__(self, token):
        self.token = token

    def server_list(self):
        """
        获取服务器列表
        :return:
        """
        return self.nova_process("/servers",None,requests.get)

    def all_server_details(self):
        """
        获取所有服务器详细信息列表
        :return:
        """
        return self.nova_process("/servers/detail",None,requests.get)

    def flaver_list(self):
        """
        获取所有flavor的列表
        :return:
        """
        return self.nova_process("/flavors/detail",None,requests.get)

    def image_list(self):
        """
        获取所有镜像的列表
        :return:
        """
        return self.nova_process("/images",None,requests.get)

class Server(Nova):
    """
    操作服务器的对象
    """
    def __init__(self, token, server_id=None):
        self.token = token
        self.server_id=server_id

    def list(self):
        """
        获取服务器列表
        :return:
        """
        return self.nova_process("/servers",None,requests.get)

    def create(self, server_name, image_id, flavor_id, security_group, publickey, personalitycontents="None"):
        """
        创建服务器
        :param server_name:服务器名
        :param image_id:镜像id
        :param flavor_id:配额id
        :param security_group:安全组id
        :param publickey:公钥名
        :param personalitycontents:非必填，干脆不要填
        :return:
        """
        security_group_s=[{'name':security_group}]
        spersonality = [ { "path":PERSONAL_PATH, "contents":base64.b64encode( personalitycontents ) } ]
        body={
            "server": {
                "name": server_name,
                "imageRef": image_id,
                "flavorRef": flavor_id,
                "metadata":
                    {
                        "Server Name": "%sMeta"%server_name
                    },
                "security_groups":security_group_s,
                "key_name": publickey,
                "personality": spersonality
            }
        }
        return self.nova_process("/servers",body,requests.post)

    def detail(self):
        """
        服务器详细信息
        :return:
        """
        if self.server_id:
            path="/servers/%s"%self.server_id
            return self.nova_process(path,None,requests.get)

    def security_list(self):
        """
        获取服务器的安全组
        :return:
        """
        if self.server_id:
            path="/servers/%s/os-security-groups"%self.server_id
            return self.nova_process(path,None,requests.get)

    def delete(self):
        """
        删除服务器
        :return:
        """
        if self.server_id:
            path="/servers/%s"%self.server_id
            return self.nova_process(path,None,requests.delete)

    def reboot(self):
        if self.server_id:
            path="/servers/%s/action"%self.server_id
            body={
                "reboot" : {
                    "type" : "HARD"
                }
            }
            return self.nova_process(path,body,requests.post)