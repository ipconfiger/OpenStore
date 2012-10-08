# encoding: utf-8

from flask import Blueprint, render_template, abort, flash, get_flashed_messages, request
from jinja2 import TemplateNotFound

index = Blueprint('index', __name__,template_folder='templates')

@index.route('/')
def index_():
    return render_template("index.html")

@index.route('/dashboard')
def dashboard():
    return render_template("dashboard.html", **locals())

@index.route('/woops')
def show_error():
    info = "\n".join(["<li>%s</li>"%msg for msg in get_flashed_messages()])
    error = "<ul>%s</ul>"%info
    next = request.args.get("next","/")
    return render_template("woops.html", **locals())