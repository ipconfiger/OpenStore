#coding=utf8
__author__ = 'alex'

from Flask import g
from models import Manager, GroupManager

def create(email,raw_password):
    manager = Manager(email, raw_password)
    g.db.add(manager)
    g.db.flush()