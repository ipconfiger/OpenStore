# encoding: utf-8
from flask import Blueprint, render_template, abort, request, g
from jinja2 import TemplateNotFound
from forms import *
from models import Product
import logging as log


product = Blueprint('product', __name__,template_folder='templates',url_prefix='/product')

@product.route('/')
def index():
    return render_template("product_list.html",**locals())

@product.route('/card')
def card():
    return render_template("card.html",**locals())


@product.route("/order")
def order_list():
    return render_template("orders.html",**locals())

@product.route("/order/<order_id>")
def order_Detail(order_id):
    return render_template("order.html",**locals())

@product.route("/manage",methods=['GET','POST'])
def manage_product():
    if request.method == "POST":
        form = ProductForm(request.form)
        if form.validate():
            ct = g.db.query(Product).filter(Product.key==form.key.data).count()
            if ct>0:
                p = g.db.query(Product).filter(Product.key==form.key.data).one()
                p.name = form.name.data
                p.cpu = int(form.cpu.data)
                p.memory = int(form.mem.data)
                p.storage = int(form.storage.data)
                p.flover_id = form.flover.data
                p.monthly_price = int(form.monthly.data)
                p.yearly_price = int(form.yearly.data)
            else:
                p=Product(form.key.data, form.name.data, form.name.data, int(form.cpu.data), int(form.mem.data), int(form.storage.data), form.flover.data, int(form.monthly.data),int(form.yearly.data))
                g.db.add(p)
            g.db.flush()
            g.db.commit()
        else:
            errors = [v[0] for k,v in form.errors.iteritems()]
    products = g.db.query(Product).all()
    return render_template("mng_product.html", **locals())


