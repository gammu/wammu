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

def IconPath(*args):
    return ImagePath('icons', *args)       

def MiscPath(*args):
    return ImagePath('misc', *args)       

def ImagePath(*args):
    return os.path.join(datapath, 'images', *args) + os.extsep + 'png'
