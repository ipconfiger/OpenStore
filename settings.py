# encoding: utf-8
import nova

DEBUG = True

SERVER_ID = "W1"

SERVER = "127.0.0.1:5000"

DB_URI = "mysql://root:123456@127.0.0.1:3306/orbit?charset=utf8"

TIMEOUT = 3600*6

SECRET_KEY = "11556654433221changge!"

SELF_KEY = 'edhsr8~w'

# Next configurations for Email Sender

MAIL_SERVER = 'smtp.163.com'

MAIL_USERNAME = 'liming0831'

MAIL_PASSWORD = '1qasw2'

DEFAULT_MAIL_SENDER = 'liming0831@163.com'

NOVA = nova.init_nova("mock")