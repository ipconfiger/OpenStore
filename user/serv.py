# encoding: utf-8
__author__ = 'alex'

import logging as log
from flask import g, url_for
from models import UserLogin, UserProfile, UserAccount, LookKey, UserTenant
from common_error import DuplicateException


def format(user_login,user_profile):
    try:
        return dict(
            id = user_login.id,
            name = user_profile.company_name,
            email = user_profile.email
        )
    except:
        pass


def check(email):
    if g.db.query(UserLogin).filter(UserLogin.login_name==email).count():
        return True

def regist(email, password):
    if check(email):
        raise DuplicateException(u"注册邮箱地址重复")
    ul = UserLogin(email, password)
    g.db.add(ul)
    g.db.flush()
    up = UserProfile(ul)
    uc = UserAccount(ul)
    g.db.add(up)
    g.db.add(uc)
    g.db.flush()
    g.db.commit()
    return ul.id

def login(email, password):
    try:
        ul = g.db.query(UserLogin).filter(UserLogin.login_name==email).one()
        if ul.cmp_password(password):
            return ul
    except Exception,e:
        log.error(e.message)

def get_user(user_id):
    try:
        ul = g.db.query(UserLogin).get(user_id)
        up = g.db.query(UserProfile).filter(UserProfile.user_id==user_id).one()
        return format(ul,up)
    except:
        pass

def get_user_login(user_id):
    return g.db.query(UserLogin).get(user_id)

def get_user_profile(user_id):
    return g.db.query(UserProfile).filter(UserProfile.user_id==user_id).one()

def get_user_account(user_id):
    return g.db.query(UserAccount).filter(UserAccount.user_id==user_id).one()

def get_user_tenant(user_id):
    return g.db.query(UserTenant).filter(UserTenant.user_id==user_id).one()

def send_lock_request(ctl,user_id):
    import uuid
    ur = LookKey(user_id, uuid.uuid4().hex)
    g.db.add(ur)
    g.db.flush()
    return url_for(ctl, key=ur.key, user_id=user_id)


def check_lock_request(user_id, key):
    urs = g.db.query(LookKey).filter(LookKey.key==key).all()
    for ur in urs:
        log.error(ur.user_id)
        if ur.user_id==int(user_id):
            return True

