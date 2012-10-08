#coding=utf8
__author__ = 'alex'

from wtforms import Form,TextField, TextAreaField, PasswordField, validators

class ProductForm(Form):
    key = TextField("product key",[validators.Required(message=u"产品编号必须填写")])
    name = TextField("name",[validators.Required(message=u"产品名称必须填写")])
    cpu = TextField("cpu",[validators.Required(message=u"cpu必须填写")])
    mem = TextField("mem",[validators.Required(message=u"内存容量必须填写")])
    storage = TextField("storage",[validators.Required(message=u"存储容量必须填写")])
    flover =TextField("flover",[validators.Required(message=u"关联ID必须填写")])
    monthly = TextField("monthly",[validators.Required(message=u"月结价格必须填写")])
    yearly = TextField("yearly",[validators.Required(message=u"年结算价格必须填写")])