# -*- coding: UTF-8 -*-
# vim: expandtab sw=4 ts=4 sts=4:
'''
Wammu - Phone manager
Config handler wrapper with various defaults, which might be platform dependant.

@var Defaults: Dictionary of default values.
@var Expandable: List of variables where path expansion should happen.
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

import sys
import os
import wx
import email.Utils
# FIXME: can be later removed
import Wammu.Data

Defaults = {
    '/Main/X': 0,
    '/Main/Y': 0,
    '/Main/Split': 160,
    '/Main/SplitRight': -200,
    '/Main/Width': 640,
    '/Main/Height': 480,
    '/Defaults/SearchRegexp': 'yes',
    '/Wammu/AutoConnect': 'no',
    '/Gammu/Model': Wammu.Data.Models[0],
    '/Gammu/Connection': Wammu.Data.Connections[0],
    '/Gammu/Device': Wammu.Data.Devices[0],
    '/Gammu/LockDevice': 'no',
    '/Debug/Show': 'no',
    '/Wammu/PhonePrefix': 'Auto',
    '/Wammu/LastPhonePrefix': '',
    '/Wammu/RefreshState': 30000,
    '/Debug/X': 0,
    '/Debug/Y': 0,
    '/Debug/Width': 400,
    '/Debug/Height': 200,
    '/Message/ScaleImage': 1,
    '/Message/Format': 'yes',
    '/Message/Concatenated': 'yes',
    '/Message/Unicode': 'no',
    '/Message/DeliveryReport': 'no',
    '/Message/16bitId': 'yes',
    '/Gammu/SyncTime': 'yes',
    '/Gammu/StartInfo': 'no',
    '/Wammu/ConfirmDelete': 'yes',
    '/Wammu/DefaultTime': '09:00:00',
    '/Wammu/DefaultDateOffset': 1,
    '/Wammu/DefaultEntries': 3,
    '/Wammu/FirstRun': -1,
    '/Wammu/TalkbackDone': 'no',
    '/IMAP/Server': '',
    '/IMAP/Login': '',
    '/IMAP/Password': '',
    }

if sys.platform == 'win32':
    # FIXME: is this really good idea?
    Defaults['/Gammu/Gammurc'] = '~/.gammurc'
else:
    import pwd
    import string

    Defaults['/Gammu/Gammurc'] = '~/.gammurc'

    name = pwd.getpwuid(os.getuid())[4]
    if ',' in name:
        name = name[:string.index(name, ',')]
    if name:
        Defaults['/User/Name'] = name

Expandable = [
    '/Gammu/Gammurc',
]

class WammuConfig:
    '''
    Wrapper class for wx.Config, which handles automatically defaults
    and allows some automatic conversion of read values (like expanding
    ~ in path).
    '''
    def __init__(self):
        # We don't want to subclass from wx.Config to hide it's API
        self.cfg = wx.Config(style = wx.CONFIG_USE_LOCAL_FILE)

    def Read(self, path):
        try:
            result = self.cfg.Read(path, Defaults[path])
        except KeyError:
            # Following line is for debugging purposes only
            print 'Warning: no default value for %s' % path
            result = self.cfg.Read(path, '')
        if path in Expandable:
            result = os.path.expanduser(result)
        return result

    def ReadInt(self, path):
        try:
            result = self.cfg.ReadInt(path, Defaults[path])
        except KeyError:
            # Following line is for debugging purposes only
            print 'Warning: no default value for %s' % path
            result = self.cfg.ReadInt(path, 0)
        return result

    def ReadFloat(self, path):
        try:
            result = self.cfg.ReadFloat(path, Defaults[path])
        except KeyError:
            # Following line is for debugging purposes only
            print 'Warning: no default value for %s' % path
            result = self.cfg.ReadFloat(path, 0)
        return result

    def Write(self, path, value):
        self.cfg.Write(path, value)

    def WriteInt(self, path, value):
        self.cfg.WriteInt(path, value)

    def WriteFloat(self, path, value):
        self.cfg.WriteFloat(path, value)

    def HasEntry(self, path):
        return self.cfg.HasEntry(path)

    def HasGroup(self, path):
        return self.cfg.HasGroup(path)
