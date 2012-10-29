#coding=utf8
__author__ = 'alex'

import logging as log
from flask import Blueprint, render_template, abort, g, request, redirect, url_for, session, flash
from jinja2 import TemplateNotFound

admin = Blueprint('admin', __name__,template_folder='templates',url_prefix='/admin')


@admin.route("/")
def index():
    return render_template("admin/index.html", **locals())

@admin.route("/login",methods=["POST","GET"])
def login():
    if request.method == "POST":
        pass
    return render_template("admin/admin_login.html", **locals())