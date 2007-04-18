#!/usr/bin/env python
# -*- coding: ISO-8859-2 -*-

from distutils.core import setup, Extension
import sys
import Wammu

try:
    import gammu
except:
    print 'You need python-gammu!'
    sys.exit(1)

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
    data_files = [('/usr/bin', ['wammu'])],
    )
