# encoding: utf-8
import os
import settings
import time
import random
import hmac
from pyDes import *
import sys, traceback
import urllib
from common_error import ValidateException

pad = lambda s, BS: s + (BS - len(s) % BS) * chr(BS - len(s) % BS)
unpad = lambda s: s[0:-ord(s[-1])]

def tob(s, enc='utf8'):
    return s.encode(enc) if isinstance(s, unicode) else bytes(s)
def touni(s, enc='utf8', err='strict'):
    return s.decode(enc, err) if isinstance(s, bytes) else unicode(s)

def format_time(t):
    return u"%s年%s月%s日%s时%s分%s秒"%(t.year,t.month,t.day,t.hour,t.minute,t.second)

def format_date(t):
    return u"%s年%s月%s日"%(t.year,t.month,t.day)

def hash_passwd(raw_password):
    salt = "".join(random.sample('abcdefghijklmnopqrstuvwxyz1234567890ABSDXFJOHDXFH',4))
    return "$".join([salt,hmac.new(salt,tob(raw_password)).hexdigest()])

def check_passwd(raw_password,enc_password):
    salt,hmac_password=tob(enc_password).split('$')
    if hmac.new(salt,tob(raw_password)).hexdigest() == hmac_password:
        return True

def serial_maker():
    t = str(int(time.time()*1000))
    salt = "".join(random.sample('QAZXSWEDCVFRTGBNHYUJMKILOP',4))
    return "%s%s%s"%(settings.SERVER_ID,t,salt)

def read_random(length):
    import random
    save_str = "abcdefghjkmnpqrstwxyz2346789"
    return random.sample(save_str,length)


def generate_code_image(size, length):
    import random
    from PIL import Image, ImageDraw, ImageFilter, ImageFont
    font_path = os.path.abspath(os.path.join(os.getcwd(),"code.ttf"))
    font = ImageFont.truetype(font_path, 18)
    words = "".join(read_random(length))
    w, h = size
    font_w, font_h = font.getsize(words)
    img = Image.new('RGB',size,(255,255,255))
    draw = ImageDraw.Draw(img)
    draw.text(((w-font_w)/3,h-font_h),words,font=font,fill=(40,40,40))
    #params = [1-float(random.randint(1,2))/100,0,0,0,1-float(random.randint(1,10))/100,float(random.randint(1,2))/500,0.001,float(random.randint(1, 2)) / 500]
    #img = img.transform(size, Image.PERSPECTIVE, params)
    img = img.filter(ImageFilter.EDGE_ENHANCE_MORE)
    return img, words


def encrypt_des(content, key):
    try:
        encryptor = des(key, CBC, "\0\0\0\0\0\0\0\0", pad=None, padmode=PAD_PKCS5)
        return encryptor.encrypt(content)
    except Exception,e:
        raise e

def decrypt_des(content, key):
    try:
        encryptor = des(key, CBC, "\0\0\0\0\0\0\0\0", pad=None, padmode=PAD_PKCS5)
        return encryptor.decrypt(content)
    except Exception,e:
        raise e


def login_required(f):
    from functools import wraps
    from flask import g, redirect, url_for
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not g.current_login_id:
            return redirect(url_for("user.login"))
        return f(*args, **kwargs)
    return decorated_function

def json_response(result,data):
    from json import dumps
    return dumps(dict(r=result,info=data))


def woops(message, next="/"):
    from flask import redirect, url_for, flash
    flash(message)
    return redirect(url_for("index.show_error", next=next))


class Frame(object):
    def __init__(self, tb):
        self.tb = tb
        frame = tb.tb_frame
        self.locals = {}
        self.locals.update(frame.f_locals)

    def print_path(self):
        return touni(traceback.format_tb(self.tb, limit=1)[0])

    def print_local(self):
        return u"\n".join(["%s=%s" % (k, self.dump_value(self.locals[k])) for k in self.locals])

    def dump_value(self, v):
        try:
            return touni(str(v))
        except:
            return u"value can not serilizable"

def print_debug(ex):
    exc_type, exc_value, exc_traceback = sys.exc_info()
    frames = []
    tb = exc_traceback
    frames.append(tb.tb_frame)
    detail = u"alex error -Exception:%s\n" % ex
    while tb.tb_next:
        tb = tb.tb_next
        fm = Frame(tb)
        detail += fm.print_path()
        detail += u"\nlocals variables:\n"
        detail += fm.print_local()
        detail += u"\n-------------------------------------------------------\n"
    return detail

def pages(item_count, page_size):
    from flask import request
    base_url = request.path
    page_id = int(request.args.get("p","1"))
    def make_url(base,pid):
        base=tob(base)
        if not pid:
            return ""
        url_slice=base.split('?')
        if len(url_slice)<2:
            return base+"?p=%s"%pid
        else:
            params=dict([(lambda i:tuple(i) if len(i)<3 else (i[0],"=".join(i[1:])))(item.split("=")) for item in url_slice[1].split('&')])
            params["p"]=pid
            return "%s?%s"%(url_slice[0],urllib.urlencode(params))

    page_count=item_count/page_size+1 if item_count%page_size else item_count/page_size
    if page_count<10:
        return [(i+1,make_url(base_url,i+1)) for i in range(page_count)]
    else:
        if page_id<5:
            return [(p,make_url(base_url,p)) for p in [1,2,3,4,5,0,page_count]]
        if page_id>(page_count-4):
            return [(p,make_url(base_url,p)) for p in [1,0,page_count-4,page_count-3,page_count-2,page_count-1,page_count]]
        return [(p,make_url(base_url,p)) for p in [1,0,page_id-2,page_id-1,page_id,page_id+1,page_id+2,0,page_count]]

