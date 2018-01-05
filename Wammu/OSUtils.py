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
OS dependant helper functions.
'''

import sys
import os
if sys.platform == 'win32':
    from win32com.shell import shellcon, shell
    import win32api
    import pywintypes


def GetUserFullName():
    '''
    Detects full user name from system information.
    '''
    if sys.platform == 'win32':
        try:
            return win32api.GetUserNameEx(win32api.NameDisplay)
        except pywintypes.error:
            return ''
    else:
        import pwd

        name = pwd.getpwuid(os.getuid())[4]
        if ',' in name:
            name = name[:name.index(',')]
        return name


def ExpandPath(orig):
    '''
    Expands user path. This is replaced on Windows, because python
    implementation has problems with encodings.
    '''
    if sys.platform == 'win32':
        if orig.startswith('~'):
            userhome = shell.SHGetFolderPath(0, shellcon.CSIDL_APPDATA, 0, 0)
            return orig.replace('~', userhome, 1)
        return orig
    else:
        if isinstance(orig, unicode):
            orig = orig.encode('utf-8')
        return os.path.expanduser(orig)
