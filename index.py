# encoding: utf-8

from flask import Blueprint, render_template, abort, flash, get_flashed_messages, request, g, session, send_file
from jinja2 import TemplateNotFound
from utils import login_required, generate_code_image, read_random
from tempfile import NamedTemporaryFile

index = Blueprint('index', __name__,template_folder='templates')

@index.route('/')
def index_():
    return render_template("index.html")

@index.route('/code')
def reg_code():
    img, code =generate_code_image((300,80),5)
    session["code"] = code
    tp = NamedTemporaryFile()
    img.save(tp.name,format="png")
    tp.seek(0)
    return send_file(tp.name,mimetype='image/png')


@index.route('/dashboard')
@login_required
def dashboard():
    from product.serv import get_unpay_order, get_user_product, get_product
    from user.serv import get_user_login
    user = get_user_login(g.current_login_id)
    orders = get_unpay_order(user)
    products = get_user_product(user)
    for userproduct in products:
        product = get_product(userproduct.product_key)
        setattr(userproduct,"product",product)
    return render_template("dashboard.html", **locals())

@index.route('/woops')
def show_error():
    info = "\n".join(["<li>%s</li>"%msg for msg in get_flashed_messages()])
    error = "<ul>%s</ul>"%info
    next = request.args.get("next","/")
    return render_template("woops.html", **locals())