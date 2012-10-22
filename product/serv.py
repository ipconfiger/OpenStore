#coding=utf8
__author__ = 'alex'

import datetime
import logging as log
from uuid import uuid4
from flask import g, url_for, session
from cPickle import loads, dumps
from models import UserLogin, UserProfile, UserAccount, Product, Order, OrderProduct, UserProduct, Favorable
from common_error import DuplicateException, EmptyException


class CardItem(object):
    """
    购物车项目类，用来描述购物车内容
    """
    def __init__(self, product_key, count, fee, favor_fee, pay_type, pay_count):
        self.id = uuid4().hex
        self.product_key = product_key
        self.pay_type = pay_type
        self.pay_count = pay_count
        self.count = count
        self.fee = fee*count*pay_count
        self.favor_fee = favor_fee*count*pay_count

    def __repr__(self):
        return u"id:%s\nproducy_key:%s\npay_type:%s\npay_count:%s\ncount:%s\nfee:%s\nfavor_fee:%s\n"%(self.id,self.product_key,self.pay_type,self.pay_count,self.count,self.fee,self.favor_fee)


class Cards(object):
    """
    购物车类，用来包含处理购物车的逻辑
    """
    def __init__(self):
        self.card_items = []
        self.total_fee = 0
        self.total_favor = 0

    def from_session(self):
        """
        从session恢复购物车内容
        """
        try:
            self.card_items = loads(session["card"]) if "card" in session else []
        except:
            self.card_items = []
        self.process()

    def add(self, carditem):
        """

        """
        self.card_items.append(carditem)
        self.save()

    def remove(self, card_id):
        self.card_items=[carditem for carditem in self.card_items if carditem.id!=card_id]
        self.save()

    def update(self, card_id, count, pay_type, pay_count):
        dn = datetime.datetime.now()
        for carditem in self.card_items:
            if carditem.id == card_id:
                carditem.count = count
                carditem.pay_type = pay_type
                carditem.pay_count = pay_count
                product = g.db.query(Product).filter(Product.key==carditem.product_key).one()
                favs = list(g.db.query(Favorable).filter(Favorable.product_key==carditem.product_key, Favorable.start<=dn, Favorable.end>=dn).all())
                favorable=favs[0] if favs else None
                fee = product.yearly_price if pay_type else product.monthly_price
                if favorable:
                    favor_fee = favorable.yearly_price if pay_type else favorable.monthly_price
                else:
                    favor_fee = fee
                fee = fee*count*pay_count
                favor_fee = favor_fee*pay_count*count
                carditem.fee = fee
                carditem.favor_fee = favor_fee
        print self.card_items
        self.save()

    def clear(self):
        self.card_items = []
        self.save()

    def process(self):
        total_fee = 0
        total_favor = 0
        for carditem in self.card_items:
            total_fee += carditem.fee
            total_favor += carditem.favor_fee
        self.total_fee = total_fee
        self.total_favor =total_favor

    def save(self):
        session["card"] = dumps(self.card_items)


    def create_order(self, user):
        dn = datetime.datetime.now()
        order = Order(user, self.total_fee, self.total_favor)
        g.db.add(order)
        g.db.flush()
        for carditem in self.card_items:
            product = g.db.query(Product).filter(Product.key==carditem.product_key).one()
            favs = list(g.db.query(Favorable).filter(Favorable.product_key==carditem.product_key, Favorable.start<=dn, Favorable.end>=dn).all())
            favorable=favs[0] if favs else None
            for i in range(carditem.count):
                if favorable:
                    orderproduct = OrderProduct(user, order, product, carditem.pay_type, carditem.pay_count, favor=favorable)
                else:
                    orderproduct = OrderProduct(user, order, product, carditem.pay_type, carditem.pay_count)
                g.db.add(orderproduct)
        g.db.flush()
        g.db.commit()
        return order.id

def create_oneitem(user, product_key, pay_type, pay_count, count):
    dn = datetime.datetime.now()
    product = g.db.query(Product).filter(Product.key==product_key).one()
    favs = list(g.db.query(Favorable).filter(Favorable.product_key==product_key, Favorable.start<=dn, Favorable.end>=dn).all())
    favorable=favs[0] if favs else None
    base_fee = count*pay_count
    fee = base_fee*product.yearly_price if pay_type else base_fee*product.monthly_price
    if favs:
        favor_fee = base_fee*favorable.yearly_price if pay_type else base_fee*favorable.monthly_price
    else:
        favor_fee = fee
    order = Order(user, fee, favor_fee)
    g.db.add(order)
    g.db.flush()
    for i in range(count):
        if favorable:
            orderproduct = OrderProduct(user, order, product, pay_type, pay_count, favor=favorable)
        else:
            orderproduct = OrderProduct(user, order, product, pay_type, pay_count)
        g.db.add(orderproduct)
    g.db.flush()
    g.db.commit()
    return order


def finish_order(order):
    from settings import NOVA
    from user import serv
    order.status = 2
    useraccount = serv.get_user_account(order.user_id)
    user = serv.get_user_login(order.user_id)
    if not useraccount.tenant_id:
        useraccount.tenant_id = NOVA.get_tenent()
    orderproducts = g.db.query(OrderProduct).filter(OrderProduct.order_id==order.id).all()
    for orderproduct in orderproducts:
        userproduct = UserProduct(user, orderproduct)
        g.db.add(userproduct)
    g.db.flush()
    g.db.commit()

def create_server(user_product_id, server_name, image_id):
    from settings import NOVA
    from user.serv import get_user_account
    userproduct = g.db.query(UserProduct).get(user_product_id)
    useraccount = get_user_account(userproduct.user_id)
    product = g.db.query(Product).filter(Product.key==userproduct.product_key).one()
    rs, server_id = NOVA.create_server(useraccount.tenant_id, product.flover_id, image_id)
    if rs:
        userproduct.image_id = image_id
        userproduct.instance_name = server_name
        userproduct.server_id = server_id
    g.db.flush()
    g.db.commit()

def get_status(user_id, server_id):
    from settings import NOVA
    from user.serv import  get_user_account
    useraccount = get_user_account(user_id)
    return NOVA.server_status(useraccount.tenant_id, server_id)



def get_unpay_order(user):
    return g.db.query(Order).filter(Order.user_id==user.id,Order.status<2).all()


def get_user_product(user):
    return g.db.query(UserProduct).filter(UserProduct.user_id==user.id).all()

def get_product(product_key):
    return g.db.query(Product).filter(Product.key==product_key).one()


def add_to_card(product_key, count, pay_type, pay_count):
    """
    添加到购物车
    :param product_key:产品编号
    :param count: 订购数量
    :param pay_type: 订购类型（按月、按年）
    :param pay_count: 时间长度（多少月，或者多少年）
    :return:空
    """
    favor = None
    dn = datetime.datetime.now()
    product = g.db.query(Product).filter(Product.key==product_key).one()
    favs = list(g.db.query(Favorable).filter(Favorable.product_key==product_key, Favorable.start<=dn, Favorable.end>=dn).all())
    favorable=favs[0] if favs else None
    fee = product.yearly_price if pay_type else product.monthly_price
    if favorable:
        favor_fee = favorable.yearly_price if pay_type else favorable.monthly_price
    else:
        favor_fee = fee

    item=CardItem(product_key, count, fee, favor_fee, pay_type, pay_count)

    cards = Cards()
    cards.from_session()
    cards.add(item)


def remove_from_card(card_id):
    cards = Cards()
    cards.from_session()
    cards.remove(card_id)


def set_item_count(card_id, count, pay_type, pay_count):
    cards = Cards()
    cards.from_session()
    cards.update(card_id,count,pay_type,pay_count)
    cards.process()
    return cards.total_fee,cards.total_favor

def card_items():
    cards = Cards()
    cards.from_session()
    cards.process()
    card_items = cards.card_items
    return cards, \
           [
           dict(
                id=carditem.id,
                product=g.db.query(Product).filter(Product.key==carditem.product_key).one(),
                count=carditem.count,
                pay_type=carditem.pay_type,
                pay_count=carditem.pay_count,
                fee=carditem.fee,
                favor_fee=carditem.favor_fee,
           ) for carditem in card_items]


def init_order():
    cards, items = card_items()
    if not items:
        raise EmptyException,"购物车是空的"


