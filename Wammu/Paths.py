# -*- coding: UTF-8 -*-
# vim: expandtab sw=4 ts=4 sts=4:
'''
Wammu - Phone manager
Data path definition and misc path functions
'''
__author__ = 'Michal Čihař'
__email__ = 'michal@cihar.com'
__license__ = '''
Copyright (c) 2003 - 2007 Michal Čihař

This program is free software; you can redistribute it and/or modify it
under the terms of the GNU General Public License version 2 as published by
the Free Software Foundation.

This program is distributed in the hope that it will be useful, but WITHOUT
ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for
more details.

You should have received a copy of the GNU General Public License along with
this program; if not, write to the Free Software Foundation, Inc.,
51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
'''

import os
import os.path
import sys

DATAPATH = os.path.join(os.path.dirname(__file__), '..')
if not os.path.exists(os.path.join(DATAPATH, 'images')):
    DATAPATH = os.path.join(sys.exec_prefix, 'share', 'Wammu')
    if not os.path.exists(os.path.join(DATAPATH, 'images')):
        print 'Could not find images, you will not see them, check your installation!'

def AppIconPath(*args):
    if sys.platform == 'win32':
        ext = 'ico'
    else:
        ext = 'png'
    p = os.path.join(*args) + os.extsep + ext
    if os.path.exists(os.path.join(sys.exec_prefix, 'share', 'pixmaps', p)):
        return os.path.join(sys.exec_prefix, 'share', 'pixmaps', p)
    else:
        return os.path.join('.', 'icon', p)

def IconPath(*args):
    return ImagePath('icons', *args)

def MiscPath(*args):
    return ImagePath('misc', *args)

def ImagePath(*args):
    return os.path.join(DATAPATH, 'images', *args) + os.extsep + 'png'
