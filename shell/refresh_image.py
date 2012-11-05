#coding=utf8
__author__ = 'alex'

from nova.nova import get_images
from models import SysImage

def main():
    db.query(SysImage).all().delete()
    for image in get_images():
        db.add(SysImage(image["id"],image["name"]))
        print image["name"], " add to system"
    db.flush()
    db.commit()
    print "all done"

