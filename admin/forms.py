#coding=utf8
__author__ = 'alex'

from wtforms import Form,TextField, TextAreaField, PasswordField, validators


class LoginForm(Form):
    login_name = TextField(
        u'login name',
        [
            validators.Required(message=u"必须输入注册邮箱"),
            validators.Length(min=4,max=50,message=u"注册邮箱长度必须大于4个字符小于50个字符"),
            validators.Email(message=u"注册邮箱格式不正确")
        ]
    )
    password = PasswordField(
        u"password",
        [
            validators.Required(message=u"必须填写密码"),
            validators.Length(min=4,max=40,message=u"密码长度必须大于4个字符，小于40个字符")
        ]
    )
    code = TextField(
        u"check code",
        [
            validators.Required(message=u"必须输入验证码")
        ]
    )
