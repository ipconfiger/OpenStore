#coding=utf8
__author__ = 'alex'
import sys
import os
sys.path.append("..")
import settings
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from utils import print_debug
from models import Base


db = DB=create_engine(settings.DB_URI,encoding = "utf-8",pool_recycle=settings.TIMEOUT,echo=False)
Session = scoped_session(sessionmaker(bind=DB))
Base.metadata.create_all(bind=db)

def main():
    if len(sys.argv)>1:
        mod_name = sys.argv[1]
        if mod_name.endswith(".py"):
            mod_name = mod_name.split(".")[0]

        mod = __import__(mod_name)
        setattr(mod,"db" ,Session())
        try:
            rs = mod.main()
            if rs:
                print "work done with error %s"%rs
            else:
                print "work done"
        except Exception, e:
            print "woops!!\n--------------------------------------"
            print print_debug(e)
    else:
        print "argument missing ,need module name!"

if __name__=="__main__":
    main()