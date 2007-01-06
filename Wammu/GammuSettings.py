# -*- coding: UTF-8 -*-
# vim: expandtab sw=4 ts=4 sts=4:
'''
Wammu - Phone manager
Wrapper for Gammu configuration
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
import sys
import wx
import re
import Wammu.Defaults

class GammuSettings:
    """
    Class wrapping gammu configuration file for reading and writing.
    """
    def __init__(self, wammu_cfg):
        """
        Reads gammu configuration and prepares it for use.

        @todo: filename is calculated wrongly.
        """
        self.wammu_cfg = wammu_cfg
        self.filename = self.wammu_cfg.Read('/Gammu/Gammurc', Wammu.Defaults.ConfigPath)
        self.config = wx.FileConfig(localFilename = self.filename, style = wx.CONFIG_USE_LOCAL_FILE)
        self.list = []

        cont, val, idx = self.config.GetFirstGroup()
        matcher = re.compile('gammu(\d*)')
        while cont:
            match = matcher.match(val)
            if match is not None:
                id = match.groups(1)[0]
                if id == '':
                    id = 0
                else:
                    id = int(id)
                name = self.config.Read('%s/name' % val, val)
                self.list.append({'Id': id, 'Name': name, 'Path': val})
            cont, val, idx = self.config.GetNextGroup(idx)

    def GetConfigs(self):
        # we need deep copy here
        result = []
        for x in self.list:
            result.append(x)
        return result

    def SetConfig(self, position, device, connection, name = None):
        found = False
        if position == 0:
            path ='gammu'
        else:
            path = 'gammu%s' % position
        for x in self.list:
            if x['Id'] == position:
                path = x['Path']
                x['Name'] = name
                found = True
                break
        self.config.SetPath(path)
        self.config.Write('port', device)
        self.config.Write('connection', connection)
        self.config.Write('name', name)
        if not found:
            self.list.append({'Id': position, 'Name': name, 'Path': path})
