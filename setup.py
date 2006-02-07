#!/usr/bin/env python
# -*- coding: UTF-8 -*-

# Wammu - Phone manager
# Copyright (c) 2003 - 2006 Michal Čihař
#
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License version 2 as published by
# the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for
# more details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA


from distutils.core import setup
import sys
import glob
import Wammu
import os.path
import os

PYTHONGAMMU_REQUIRED = (0,10)

if os.getenv('SKIPGAMMUCHECK') == 'yes':
    print 'Skipping Gammu check, expecting you know what you are doing!'
else:
    try:
        import gammu
    except ImportError:
        print 'You need python-gammu!'
        print 'You can get it from <http://www.cihar.com/gammu/python/>'
        sys.exit(1)
    pygver = tuple(map(int, gammu.Version()[1].split('.')))
    if  pygver < PYTHONGAMMU_REQUIRED:
        print 'You need python-gammu at least %s!' % '.'.join(map(str, PYTHONGAMMU_REQUIRED))
        print 'You can get it from <http://www.cihar.com/gammu/python/>'
        sys.exit(1)

if os.getenv('SKIPWXCHECK') == 'yes':
    print 'Skipping wx check, expecting you know what you are doing!'
else:
    try:
        import wx
    except ImportError:
        print 'You need wxPython!'
        print 'You can get it from <http://www.wxpython.org>'
        sys.exit(1)
    if wx.VERSION < (2,4,1,2):
        print 'You need at least wxPython 2.4.1.2!'
        print 'You can get it from <http://www.wxpython.org>'
        sys.exit(1)

try:
    import gnomebt.controller
except ImportError:
    try:
        import bluetooth
    except ImportError:
        print 'WARNING: neither GNOME Bluetooth nor PyBluez found, without those you can not search for bluetooth devices'
        print 'GNOME Bluetooth can be downloaded from <http://usefulinc.com/software/gnome-bluetooth>'
        print 'PyBluez can be downloaded from <http://org.csail.mit.edu/pybluez/>'

setup(name="wammu",
    version = Wammu.__version__,
    description = "GUI for gammu.",
    long_description = "Phone manager built on top of python-gammu. Supports many phones.",
    author = "Michal Čihař",
    author_email = "michal@cihar.com",
    maintainer = "Michal Čihař",
    maintainer_email = "michal@cihar.com",
    url = "http://cihar.com/gammu/wammu",
    license = "GPL",
    classifiers = [
        'Development Status :: 5 - Production/Stable',
        'Environment :: Win32 (MS Windows)',
        'Environment :: X11 Applications :: GTK',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Operating System :: Microsoft :: Windows :: Windows 95/98/ME',
        'Operating System :: Microsoft :: Windows :: Windows NT/2000/XP',
        'Operating System :: POSIX',
        'Operating System :: Unix',
        'Programming Language :: Python',
        'Topic :: Communications :: Telephony',
        'Topic :: Office/Business :: Scheduling',
        'Topic :: Utilities',
        'Translations :: English',
        'Translations :: Czech'

    ],
    packages = ['Wammu', 'Wammu.wxcomp'],
    scripts = ['wammu'],
    data_files = [
        (os.path.join('share','Wammu','images','icons'), glob.glob('images/icons/*.png')),
        (os.path.join('share','Wammu','images','misc'), glob.glob('images/misc/*.png')),
        (os.path.join('share','locale','cs','LC_MESSAGES'), ['locale/cs/LC_MESSAGES/wammu.mo']),
        (os.path.join('share','applications'), ['wammu.desktop']),
        (os.path.join('share','pixmaps'), ['wammu.png', 'wammu.xpm']),
        (os.path.join('share','man','man1'), ['wammu.1'])
        ]
    )
