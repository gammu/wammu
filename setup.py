#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from distutils.core import setup
import sys
import glob
import Wammu
import os.path
import os

if os.getenv('SKIPGAMMUCHECK') == 'yes':
    print 'Skipping Gammu check, expecting you know what you are doing!'
else:
    try:
        import gammu
    except:
        print 'You need python-gammu!'
        sys.exit(1)
    if gammu.Version()[1] < '0.4':
        print 'You need python-gammu at least 0.4!'
        sys.exit(1)

if os.getenv('SKIPWXCHECK') == 'yes':
    print 'Skipping wx check, expecting you know what you are doing!'
else:
    try:
        import wx
    except:
        print 'You need wxPython!'
        sys.exit(1)
    if wx.VERSION < (2,4,1,2):
        print 'You need at least wxPython 2.4.1.2!'
        sys.exit(1)
     
       

setup(name="wammu",
    version = Wammu.__version__,
    description = "GUI for gammu.",
    long_description = "Phone manager built on top of python-gammu. Supports many phones.",
    author = "Michal Čihař",
    author_email = "michal@cihar.com",
    url = "http://cihar.com/gammu/wammu",
    license = "GPL",
    packages = ['Wammu', 'Wammu.wxcomp'],
    scripts = ['wammu'],
    data_files = [
        (os.path.join('share','Wammu','images','icons'), glob.glob('images/icons/*.png')),
        (os.path.join('share','Wammu','images','misc'), glob.glob('images/misc/*.png')),
        (os.path.join('share','locale','cs','LC_MESSAGES'), ['locale/cs/LC_MESSAGES/wammu.mo']),
        ]
    )
