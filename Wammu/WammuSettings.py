# -*- coding: UTF-8 -*-
#
# Copyright © 2003 - 2015 Michal Čihař <michal@cihar.com>
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
#
# vim: expandtab sw=4 ts=4 sts=4:
'''
Wammu - Phone manager
Config handler wrapper with various defaults, which might be platform
dependant.

@var DEFAULT_CONFIG: Dictionary of default values.
@var EXPANDABLE_CONFIGS: List of variables where path expansion should happen.
'''

import os
import wx
import Wammu.GammuSettings
import Wammu.OSUtils

DEFAULT_CONFIG = {
    '/Main/X': 0,
    '/Main/Y': 0,
    '/Main/Split': 160,
    '/Main/SplitRight': -200,
    '/Main/Width': 640,
    '/Main/Height': 480,
    '/Defaults/SearchType': 0,
    '/Defaults/Type-contact-MemoryType': 'SM',
    '/Defaults/Type-calendar-Type': 'MEETING',
    '/Defaults/Type-todo-Priority': 'Medium',
    '/Defaults/Entry-contact-0': 'Text_Name',
    '/Defaults/Entry-contact-1': 'Number_General',
    '/Defaults/Entry-todo-0': 'TEXT',
    '/Defaults/Entry-calendar-0': 'TEXT',
    '/Defaults/Entry-calendar-1': 'START_DATETIME',
    '/Defaults/Entry-calendar-2': 'END_DATETIME',
    '/Wammu/AutoConnect': 'no',
    '/Gammu/LockDevice': False,
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
    '/Gammu/SyncTime': True,
    '/Gammu/StartInfo': True,
    '/Wammu/ConfirmDelete': 'yes',
    '/Wammu/DefaultTime': '09:00:00',
    '/Wammu/DefaultDateOffset': 1,
    '/Wammu/DefaultEntries': 3,
    '/Wammu/FirstRun': -1,
    '/Wammu/RunCounter': 0,
    '/Wammu/TalkbackDone': 'no',
    '/Wammu/NameFormat': 'auto',
    '/Wammu/NameFormatString': '%(FirstName)s %(LastName)s (%(Company)s)',
    '/IMAP/Server': '',
    '/IMAP/Port': '',
    '/IMAP/Login': '',
    '/IMAP/Password': '',
    '/IMAP/RememberPassword': 'no',
    '/IMAP/UseSSL': 'yes',
    '/IMAP/OnlyNewMessages': 'yes',
    '/IMAP/BackupStateRead': 'yes',
    '/IMAP/BackupStateSent': 'yes',
    '/IMAP/BackupStateUnread': 'yes',
    '/IMAP/BackupStateUnsent': 'yes',
    '/MessageExport/From': 'Wammu <wammu@wammu.sms>',
    '/Gammu/Section': 0,
    '/User/Name': Wammu.OSUtils.GetUserFullName(),
    '/Gammu/Gammurc': os.path.join(u'~', u'.gammurc'),
    '/Hacks/MaxEmptyGuess': 50,
    '/Hacks/MaxEmptyKnown': 100,
    }


EXPANDABLE_CONFIGS = [
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
        self.cfg = wx.Config(
            appName='Wammu',
            style=wx.CONFIG_USE_LOCAL_FILE
        )
        self.gammu = None
        self.InitGammu()

    def Flush(self):
        self.cfg.Flush()

    def InitGammu(self, path=None):
        '''
        Initializes gammu configuration as sub part of this class.
        '''
        self.gammu = Wammu.GammuSettings.GammuSettings(self, path)

    def Read(self, path, expand=True):
        '''
        Reads string option from configuration.
        '''
        try:
            result = self.cfg.Read(path, DEFAULT_CONFIG[path])
        except KeyError:
            # Following line is for debugging purposes only
            # print 'Warning: no default value for %s' % path
            result = self.cfg.Read(path, '')
        if expand and path in EXPANDABLE_CONFIGS:
            result = Wammu.OSUtils.ExpandPath(result)
        return result

    def ReadInt(self, path):
        '''
        Reads integer option from configuration.
        '''
        try:
            result = self.cfg.ReadInt(path, DEFAULT_CONFIG[path])
        except KeyError:
            # Following line is for debugging purposes only
            # print 'Warning: no default value for %s' % path
            result = self.cfg.ReadInt(path, 0)
        return result

    def ReadFloat(self, path):
        '''
        Reads float option from configuration.
        '''
        try:
            result = self.cfg.ReadFloat(path, DEFAULT_CONFIG[path])
        except KeyError:
            # Following line is for debugging purposes only
            # print 'Warning: no default value for %s' % path
            result = self.cfg.ReadFloat(path, 0)
        return result

    def ReadBool(self, path):
        '''
        Reads boolean option from configuration.
        '''
        try:
            result = self.cfg.ReadBool(path, DEFAULT_CONFIG[path])
        except KeyError:
            # Following line is for debugging purposes only
            # print 'Warning: no default value for %s' % path
            result = self.cfg.ReadBool(path, 0)
        return result

    def Write(self, path, value):
        '''
        Writes string option to configuration.
        '''
        self.cfg.Write(path, value)

    def WriteInt(self, path, value):
        '''
        Writes integer option to configuration.
        '''
        self.cfg.WriteInt(path, value)

    def WriteFloat(self, path, value):
        '''
        Writes float option to configuration.
        '''
        self.cfg.WriteFloat(path, value)

    def WriteBool(self, path, value):
        '''
        Writes boolean option to configuration.
        '''
        self.cfg.WriteBool(path, value)

    def HasEntry(self, path):
        '''
        Checks whether configuration has some entry.
        '''
        return self.cfg.HasEntry(path)
