# -*- coding: UTF-8 -*-
#
# Copyright © 2003 - 2018 Michal Čihař <michal@cihar.com>
#
# This file is part of Wammu <https://wammu.eu/>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
'''
Wammu - Phone manager
Data path definition and misc path functions
'''
from __future__ import print_function

import os
import os.path
import sys

POSSIBLE_PATHS = [
    # systemwide in default prefix
    os.path.join(sys.exec_prefix, 'share', 'Wammu'),
    # systemwide, default distutils
    os.path.join(sys.exec_prefix, 'local', 'share', 'Wammu'),
    # systemwide installation in custom prefix
    os.path.join(os.path.dirname(__file__).replace('lib/python2.7/site-packages/Wammu', ''), 'share', 'Wammu'),
    # systemwide installation in custom prefix on Debian
    os.path.join(os.path.dirname(__file__).replace('lib/python2.7/dist-packages/Wammu', ''), 'share', 'Wammu'),
     # Local directory
    os.path.join(os.path.dirname(__file__), '..'),
]

def CheckImagesPath(path):
    return (
        os.path.exists(os.path.join(path, 'images')) and
        os.path.exists(os.path.join(path, 'images', 'icons', 'message.png'))
    )

for DATAPATH in POSSIBLE_PATHS:
    if CheckImagesPath(DATAPATH):
        break

if not CheckImagesPath(DATAPATH):
    print('Could not find images, check your installation!')
    sys.exit(1)

def AppIconPath(*args):
    if sys.platform == 'win32':
        ext = 'ico'
    else:
        ext = 'png'
    p = os.path.join(*args) + os.extsep + ext
    if os.path.exists(os.path.join(sys.exec_prefix, 'share', 'pixmaps', p)):
        return os.path.join(sys.exec_prefix, 'share', 'pixmaps', p)
    elif os.path.exists(os.path.join(DATAPATH, '..', 'pixmaps', p)):
        return os.path.join(DATAPATH, '..', 'pixmaps', p)
    elif os.path.exists(os.path.join('usr', 'share', 'pixmaps', p)):
        return os.path.join('usr', 'share', 'pixmaps', p)
    else:
        return os.path.join('.', 'icon', p)

def IconPath(*args):
    return ImagePath('icons', *args)

def MiscPath(*args):
    return ImagePath('misc', *args)

def ImagePath(*args):
    return os.path.join(DATAPATH, 'images', *args) + os.extsep + 'png'
