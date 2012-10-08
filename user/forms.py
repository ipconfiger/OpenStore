# encoding: utf-8
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


class RegistForm(Form):
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
            validators.Length(min=4,max=40,message=u"密码长度必须大于4个字符，小于40个字符"),
            validators.EqualTo("confirm_password",message=u"两次密码输入必须一致")
        ]
    )
    confirm_password = PasswordField(
        u"confirm password",
        [
            validators.Required(message=u"必须重复输入密码"),
        ]
    )

class ProfileForm(Form):
    company_name = TextField(
        u"for the real name",
        [
            validators.Required(message=u"公司名称必须填写"),
            validators.Length(min=4,max=20,message=u"公司名称长度必须大于4个，小于20个字符")
        ]
    )
    contact = TextField(u"the contact name")
    mobile = TextField(
        u"contact phone",
        [
            validators.Length(min=6,max=11,message=u"电话号码貌似长度不对哦"),
        ]
    )
    addr = TextField(u"contact addr")


class PasswordForm(Form):
    oldpassword = PasswordField(
        u"old password",
        [
            validators.Required(message=u"必须填写密码"),
            validators.Length(min=4,max=40,message=u"密码长度必须大于4个字符，小于40个字符")
        ]
    )
    newpassword = PasswordField(
        u"new password",
        [
            validators.Length(min=4,max=40,message=u"密码长度必须在大于4个字符，小于40个字符"),
            validators.EqualTo("confirmpassword",message=u"重复输入的密码必须和第一次输入的密码一致")
        ]
    )
    confirmpassword = PasswordField(u"confirm password")

class EmailForm(Form):
    password = PasswordField(
        u"password",
        [
            validators.Required(message=u"必须填写密码"),
            validators.Length(min=4,max=40,message=u"密码长度必须大于4个字符，小于40个字符")
        ]
    )
    email = TextField(
        u'login name',
        [
            validators.Required(message=u"必须输入注册邮箱"),
            validators.Length(min=4,max=50,message=u"注册邮箱长度必须大于4个字符小于50个字符"),
            validators.Email(message=u"注册邮箱格式不正确")
        ]
    )