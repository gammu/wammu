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
'''
Data path definition and misc path functions
'''

import os
import os.path
import sys

datapath = os.path.join(sys.exec_prefix, 'share', 'Wammu')
if not os.path.exists(os.path.join(datapath, 'images')):
    if not os.path.exists('images'):
        print 'Could not find images, you will not see them, check your installation!'
    else:
        datapath = os.getcwd()

def AppIconPath(*args):
    p = os.path.join(*args) + os.extsep + 'png'
    if os.path.exists(os.path.join('/usr', 'share', 'pixmaps', p)):
        return os.path.join('/usr', 'share', 'pixmaps', p)
    else:
        return os.path.join('.', p)

def IconPath(*args):
    return ImagePath('icons', *args)

def MiscPath(*args):
    return ImagePath('misc', *args)

def ImagePath(*args):
    return os.path.join(datapath, 'images', *args) + os.extsep + 'png'
