#!/usr/bin/env python
# -*- coding: ISO-8859-2 -*-

from distutils.core import setup
import sys
import glob
import Wammu
import os.path
import os

try:
    import gammu
except:
    print 'You need python-gammu!'
    sys.exit(1)

if os.getenv('SKIPWXCHECK') == 'yes':
    print 'Skipping wx check, expecting you know what you are doing!'
else:
    try:
        import wx
    except:
        print 'You need wxPython!'
        sys.exit(1)
       

setup(name="wammu",
    version = Wammu.__version__,
    description = "GUI for gammu.",
    author = "Michal Čihař",
    author_email = "michal@cihar.com",
    url = "http://cihar.com/gammu/wammu",
    license = "GPL",
    packages = ['Wammu'],
    scripts = ['wammu'],
    data_files = [
        (os.path.join('share','Wammu','images','icons'), glob.glob('images/icons/*.png')),
        (os.path.join('share','Wammu','images','misc'), glob.glob('images/misc/*.png')),
        ]
    )
