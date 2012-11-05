#coding=utf8
__author__ = 'alex'

from nova.nova import get_images
from models import SysImage

def main():
    db.query(SysImage).filter(SysImage.disabled==False).delete()
    db.query(SysImage).filter(SysImage.disabled==True).delete()
    for image in get_images():
        db.add(SysImage(image["id"],image["name"]))
        print image["name"], " add to system"
    db.flush()
    db.commit()
    print "all done"

