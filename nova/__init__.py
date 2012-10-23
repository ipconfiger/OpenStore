#coding=utf8
__author__ = 'alex'
import mock
import nova
import settings

def api():
    if settings.NOVA=="mock":
        return mock
    else:
        return nova