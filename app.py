# encoding: utf-8
import sys
import os
import time
import logging as log
from flask import Flask, g, session
import settings
from index import index
from user.views import user
from user.serv import get_user
from product.views import product
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker, scoped_session
from flask_mail import Mail

dir_path = os.getcwd()
if dir_path not in sys.path:
    sys.path.append(dir_path)


app = Flask(__name__)
app.config.from_object(settings)
app.register_blueprint(index)
app.register_blueprint(user)
app.register_blueprint(product)

mail = Mail(app)

DB=create_engine(settings.DB_URI,encoding = "utf-8",pool_recycle=settings.TIMEOUT,echo=False)
Session = scoped_session(sessionmaker(bind=DB))

def init_db():
    from models import Base
    Base.metadata.create_all(bind=DB)

@app.before_request
def before_request():
    """
    在请求执行前执行
    """
    g.mail = mail
    g.db = Session()
    user_id = session.get('user_id')
    if user_id:
        g.current_login_id = user_id
        g.user = get_user(user_id)
    else:
        g.current_login_id = None
        g.user = None


@app.teardown_request
def tear_down(exception=None):
    """
    当请求结束的时候执行
    """
    try:
        if exception:
            g.db.rollback()
        else:
            g.db.commit()
        g.db.close()
    except Exception, e:
        log.error(e.message)

if __name__ == '__main__':
    init_db()
    app.run()