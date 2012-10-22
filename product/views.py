# encoding: utf-8
import datetime
import serv
from utils import print_debug, json_response, woops, login_required, pages
from json import dumps
from flask import Blueprint, render_template, abort, request, g, redirect, url_for, session
from jinja2 import TemplateNotFound
from forms import *
from models import Product, Favorable, Order, OrderProduct, UserProduct
from user.serv import get_user_login
import logging as log


product = Blueprint('product', __name__,template_folder='templates',url_prefix='/product')

@product.app_template_filter(name="order_status")
def order_status(status_code):
    """
    0-下单未付款 1-已付款 2－已确认付款 10－用户自己取消 11-操作员取消 12-系统自动取消 13-失效
    :param status_code:
    :return:
    """
    status = {
        0:u"已下单未付款",
        1:u"已确认订单",
        2:u"已确认付款",
        10:u"用户自己取消",
        11:u"操作员取消",
        12:u"系统自动取消",
    }
    return status[status_code]

@product.app_template_filter(name="pay_type")
def show_pay_type(type):
    return u"年" if type else u"月"

@product.app_template_filter(name="mems")
def show_memory(m):
    if m<1024:
        return "%sM"%m
    return "%02.1fG"%(m/1024.0)


@product.route('/')
def index():
    dn = datetime.datetime.now()
    products = g.db.query(Product).all()
    for product in products:
        favs = list(g.db.query(Favorable).filter(Favorable.product_key==product.key, Favorable.start<=dn, Favorable.end>=dn).all())
        favorable=favs[0] if favs else None
        if favorable:
            setattr(product,"has_favor",True)
            setattr(product,"favor_monthly_price",favorable.monthly_price)
            setattr(product,"favor_yearly_price",favorable.yearly_price)
    return render_template("product_list.html",**locals())

@product.route('/card',methods=["GET"])
def card():
    dn = datetime.datetime.now()
    cards, card_items = serv.card_items()
    for carditem in card_items:
        favs = list(g.db.query(Favorable).filter(Favorable.product_key==carditem["product"].key, Favorable.start<=dn, Favorable.end>=dn).all())
        favorable=favs[0] if favs else None
        if favorable:
            setattr(carditem["product"],"has_favor",True)
            setattr(carditem["product"],"favor_monthly_price",favorable.monthly_price)
            setattr(carditem["product"],"favor_yearly_price",favorable.yearly_price)
    return render_template("card.html",**locals())


@product.route("/order")
def order_list():
    user = get_user_login(g.current_login_id)
    q = g.db.query(Order).filter(Order.user_id==user.id).order_by(Order.id.desc())
    page_size = 20
    total = q.count()
    start = (int(request.args.get("p","1")) - 1) * page_size
    orders = q[start:start+page_size]
    pids = pages(total,page_size)
    return render_template("orders.html",**locals())

@product.route("/order/<order_id>")
def order_Detail(order_id):
    order = g.db.query(Order).get(order_id)
    orderproducts = g.db.query(OrderProduct).filter(OrderProduct.order_id==int(order_id)).all()
    return render_template("order.html",**locals())

@product.route("/order_done/<order_id>")
@login_required
def order_done(order_id):
    order = g.db.query(Order).get(order_id)
    return render_template("order_done.html", **locals())


@product.route("/card",methods=["POST"])
def add_to_card():
    try:
        product_key = request.form["p"]
        count = int(request.form["c"])
        pay_type = int(request.form['t'])
        pay_count = int(request.form["tl"])
        serv.add_to_card(product_key, count,pay_type,pay_count)
        return json_response(True,"")
    except Exception, e:
        log.error(print_debug(e))
        return json_response(False,u"未知异常%s"%request.form["c"])

@product.route("/card",methods=["PUT"])
def change_item_count():
    try:
        card_id = request.form.get("id")
        count = int(request.form.get("c"))
        pay_type = int(request.form.get("pt"))
        pay_count = int(request.form.get("pc"))
        fee,favor_fee = serv.set_item_count(card_id, count, pay_type, pay_count)
        return json_response(True,{'fee':fee,'favor_fee':favor_fee})
    except Exception, e:
        log.error(print_debug(e))
        return json_response(False,u"未知异常")

@product.route("/card", methods=["DELETE"])
def remove_from_card():
    try:
        card_id = request.args["id"].strip()
        serv.remove_from_card(card_id)
        return json_response(True,"")
    except Exception, e:
        log.error(print_debug(e))
        return json_response(False,u"未知异常")

@product.route("/card/clear")
def clear_card():
    from cPickle import dumps
    session["card"] = dumps({})
    return redirect(url_for('product.card'))

@product.route("/order",methods=["POST"])
@login_required
def create_order():
    try:
        user = get_user_login(g.current_login_id)
        cards = serv.Cards()
        cards.from_session()
        order_id = cards.create_order(user)
        cards.clear()
        return redirect(url_for("product.order_done",order_id=order_id))
    except Exception, e:
        g.db.rollback()
        log.error(print_debug(e))
        return woops(u"创建订单失败")

@product.route("/one/order",methods=["POST"])
@login_required
def create_one_order():
    try:
        user = get_user_login(g.current_login_id)
        order = serv.create_oneitem(user, request.form["key"], int(request.form["pay_type"]),int(request.form["pay_count"]),int(request.form["count"]))
        return redirect(url_for("product.order_done",order_id=order.id))
    except Exception, e:
        g.db.rollback()
        log.error(print_debug(e))
        return woops(u"创建订单失败")


@product.route("/order_manage/<order_id>",methods=["POST","GET"])
@login_required
def operate_order(order_id):
    action = int(request.args.get("status"))
    order = g.db.query(Order).filter(Order.serial_number==order_id).one()
    if action==2:
        try:
            serv.finish_order(order)
            return "ok"
        except Exception, e:
            g.db.rollback()
            log.error(print_debug(e))
            return woops(u"完成订单失败")


@product.route("/order_manage",methods=["GET"])
def manage_orders():
    q = g.db.query(Order).order_by(Order.id.desc())
    page_size = 20
    total = q.count()
    start = (int(request.args.get("p","1")) - 1) * page_size
    orders = q[start:start+page_size]
    pids = pages(total,page_size)
    return render_template("", **locals())

@product.route("/server",methods=["POST"])
@login_required
def create_server():
    user_product_id = int(request.form.get("up_id"))
    server_name = request.form.get("name")
    image_id = request.form.get("image_id")
    try:
        serv.create_server(user_product_id, server_name, image_id)
        return json_response(True,{})
    except Exception, ex:
        log.error(print_debug(ex))
        g.db.rollback()
        return json_response(False,u"未知异常")

@product.route("/server/<server_id>",methods=["GET"])
@login_required
def server_status(server_id):
    from user.serv import get_user_account
    user_id = g.current_user_id
    return json_response(True,serv.get_status(user_id, server_id))



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


