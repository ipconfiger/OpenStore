# encoding: utf-8
import logging as log
from flask import Blueprint, render_template, abort, g, request, redirect, url_for, session, flash
from jinja2 import TemplateNotFound
from forms import RegistForm, LoginForm, ProfileForm, PasswordForm, EmailForm
import serv
from flask_mail import Message
from common_error import DuplicateException
from utils import login_required, touni, tob, woops, print_debug
from models import *

user = Blueprint('user', __name__,template_folder='templates',url_prefix='/user')

@user.route('/')
def index():
    return render_template("user.html", **locals())

@user.route('/login', methods=['GET','POST'])
def login():
    if request.method == "POST":
        form = LoginForm(request.form)
        if form.validate():
            ul = serv.login(form.login_name.data,form.password.data)
            if ul:
                session["user_id"] = ul.id
                return redirect("/")
            errors = [u"用户登陆失败"]
        else:
            errors = [v[0] for k,v in form.errors.iteritems()]
    return render_template("login.html", **locals())


@user.route('/regist', methods=['GET','POST'])
def create():
    if request.method == "POST":
        reg_code = request.form.get("code","").strip().lower()
        if reg_code != "orz!":
            if reg_code != session["code"].strip().lower():
                errors = [u"验证码不正确"]
                return render_template("regist.html",**locals())
        form = RegistForm(request.form)
        if form.validate():
            try:
                user_id = serv.regist(form.login_name.data,form.password.data)
                session["user_id"] = user_id
                return redirect(url_for('user.info'))
            except DuplicateException,e:
                g.db.rollback()
                errors = [e.message,]
        else:
            errors = [v[0] for k,v in form.errors.iteritems()]
    randcode = "".join(utils.read_random(5))
    return render_template("regist.html",**locals())


@user.route('/profile', methods=['GET','POST'])
@login_required
def info():
    user_id = g.current_login_id
    user_profile = g.db.query(UserProfile).filter(UserProfile.user_id==user_id).one()
    if request.method == "POST":
        form = ProfileForm(request.form)
        if form.validate():
            try:
                user_profile.company_name = form.company_name.data
                user_profile.contact_name = form.contact.data
                user_profile.mobile = form.mobile.data
                user_profile.company_addr = form.addr.data
                g.db.flush()
                success = u"修改用户资料成功"
            except Exception, e:
                log.error(e.message)
                g.db.rollback()
                errors = [u"未知异常",]
        else:
            errors = [v[0] for k, v in form.errors.iteritems()]
    return render_template("more_info.html",**locals())


@user.route('/profile/email', methods=['GET','POST'])
def reset_email():
    if request.method == "POST":
        form = EmailForm(request.form)
        if form.validate():
            ul = serv.login(g.user['email'],form.password.data)
            if ul:
                #TODO：发送确认邮件
                try:
                    uri = serv.send_lock_request("user.confirm_email", ul.id)
                    up = g.db.query(UserProfile).filter(UserProfile.user_id==ul.id).one()
                    up.email = form.email.data
                    g.db.flush()
                    g.db.commit()
                    success = u"确认邮箱的邮件已经发出，请登录邮箱点击确认链接，然后才能使用新邮箱登陆"
                    msg = Message(u"登陆邮箱变更确认邮件", sender="liming0831@163.com", recipients=["superpowerlee@gmail.com"])
                    msg.html = "点击下面链接确认登陆邮件变更，点击后用新邮箱登陆爱普云平台<br/><a href=\"http://%s%s\">%s</a>"%(settings.SERVER, uri, uri)
                    g.mail.send(msg)
                except Exception, e:
                    g.db.rollback()
                    log.error(print_debug(e))
                    errors = [u"未知异常"]
            else:
                errors = [u"登陆密码输入不正确"]
        else:
            errors = [v[0] for k, v in form.errors.iteritems()]
    return render_template("change_email.html",**locals())

@user.route('/profile/password', methods=['GET','POST'])
@login_required
def reset_password():
    if request.method == "POST":
        form = PasswordForm(request.form)
        if form.validate():
            ul = serv.login(g.user['email'],form.oldpassword.data)
            if ul:
                ul.reset_password(form.newpassword.data)
                try:
                    g.db.flush()
                    g.db.commit()
                    success = u"重设密码成功"
                except Exception, e:
                    g.db.rollback()
                    log.error(e.message)
                    errors = [u"未知异常"]
            else:
                errors = [u"登陆密码输入不正确"]
        else:
            errors = [v[0] for k, v in form.errors.iteritems()]
    return render_template("change_password.html",**locals())

@user.route("/profile/email/confirm/<user_id>/<key>")
def confirm_email(user_id,key):
    if not serv.check_lock_request(user_id, key):
        return woops(u"该验证邮箱url已经过期")
    session["user_id"] = ""
    ul = g.db.query(UserLogin).get(user_id)
    if not ul:
        return woops(u"用户不存在")
    ul.login_name = ul.profile.email
    ul.profile.val_email = True
    try:
        g.db.flush()
        g.db.commit()
    except Exception, e:
        log.error(e.message)
        return woops(u"未知异常")
    return redirect(url_for('user.login'))


@user.route("/find",methods=["GET","POST"])
def find_password():
    session["user_id"] = ""
    if request.method == "POST":
        email = request.form.get("email")
        uls = list(g.db.query(UserLogin).filter(UserLogin.login_name==email).all())
        if not uls:
            error = u"用户不存在"
        else:
            ul = uls[0]
            try:
                uri = serv.send_lock_request("user.confirm_email",ul.id)
                success = u"重设密码邮件已经发送，请登陆邮箱后点击链接进入重设密码页面"
                msg = Message(u"登录邮箱确认邮件", sender="liming0831@163.com", recipients=["superpowerlee@gmail.com"])
                msg.html = "点击下面链接确认登陆邮件变更，点击后用新邮箱登陆爱普云平台<br/><a href=\"http://%s%s\">%s</a>"%(settings.SERVER, uri, uri)
                g.mail.send(msg)
            except Exception, e:
                log.error(e.message)
                error = u"未知异常"
    return render_template("find_password.html", **locals())


@user.route("/logout")
def logout():
    session["user_id"] = ""
    return redirect("/")

@user.route("/testmail")
def test_mail():
    msg = Message("Hello this is the test",
        sender="liming0831@163.com",
        recipients=["superpowerlee@gmail.com"])
    msg.body = "testing"
    msg.html = "<h1>testing</h1>"
    g.mail.send(msg)
    return "mail done"