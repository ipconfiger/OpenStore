#coding=utf8
__author__ = 'alex'
import mock
import nova

def init_nova(type):
    if type=="mock":
        return mock
    else:
        return nova