#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# Wammu - Phone manager
# Copyright (c) 2003-4 Michal Cihar 
#
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 2 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MER- CHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for
# more details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc., 59 Temple
# Place, Suite 330, Boston, MA 02111-1307 USA


from distutils.core import setup
import sys
import glob
import Wammu
import os.path
import os

PYTHONGAMMU_REQUIRED = (0,4,1)

if os.getenv('SKIPGAMMUCHECK') == 'yes':
    print 'Skipping Gammu check, expecting you know what you are doing!'
else:
    try:
        import gammu
    except:
        print 'You need python-gammu!'
        sys.exit(1)
    pygver = tuple(map(int, gammu.Version()[1].split('.')))
    if  pygver < PYTHONGAMMU_REQUIRED:
        print 'You need python-gammu at least %s!' % '.'.join(map(str, PYTHONGAMMU_REQUIRED))
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
