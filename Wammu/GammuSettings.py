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
Wrapper for Gammu configuration
'''

import wx
import re
from Wammu.Locales import ugettext as _


class GammuSettings:
    '''
    Class wrapping gammu configuration file for reading and writing.
    '''
    def __init__(self, wammu_cfg, path=None):
        '''
        Reads gammu configuration and prepares it for use.
        '''
        self.wammu_cfg = wammu_cfg
        if path is not None:
            self.filename = path
        else:
            self.filename = self.wammu_cfg.Read('/Gammu/Gammurc')
        self.config = wx.FileConfig(
            localFilename=self.filename,
            style=wx.CONFIG_USE_LOCAL_FILE
        )
        self.list = []

        cont, val, idx = self.config.GetFirstGroup()
        matcher = re.compile('gammu(\d*)')
        while cont:
            match = matcher.match(val)
            if match is not None:
                index = match.groups(1)[0]
                if index == '':
                    index = 0
                else:
                    index = int(index)
                name = self.config.Read('%s/name' % val, val)
                self.list.append({'Id': index, 'Name': name, 'Path': val})
            cont, val, idx = self.config.GetNextGroup(idx)

    def GetConfigs(self):
        '''
        Returns copy of list of configuration settings.
        '''
        # we need deep copy here
        result = []
        for config in self.list:
            result.append(config)
        return result

    def GetConfig(self, position):
        '''
        Returns complete configuration.
        '''
        if position == 0:
            path = 'gammu'
        else:
            path = 'gammu%s' % position
        device = self.config.Read('/%s/device' % path)
        if device == '':
            device = self.config.Read('/%s/port' % path)
        connection = self.config.Read('/%s/connection' % path)
        model = self.config.Read('/%s/model' % path)
        name = self.config.Read('/%s/name' % path)
        return {
            'Name': name,
            'Device': device,
            'Connection': connection,
            'Model': model
        }

    def SetConfig(self, position, device, connection, name=None, model=None):
        '''
        Set configuration at defined position.
        '''
        found = False
        if position == 0:
            path = 'gammu'
        else:
            path = 'gammu%s' % position
        for config in self.list:
            if config['Id'] == position:
                path = config['Path']
                config['Name'] = name
                found = True
                break
        self.config.Write('/%s/port' % path, device)
        self.config.Write('/%s/connection' % path, connection)
        if name is not None:
            self.config.Write('/%s/name' % path, name)
        if model is not None:
            self.config.Write('/%s/model' % path, model)
        if not found:
            self.list.append({'Id': position, 'Name': name, 'Path': path})
        self.config.Flush()

    def FirstFree(self):
        '''
        Find first free entry in configuration file.
        '''
        idxmap = {}
        first_free = None
        for config in self.list:
            idxmap[config['Id']] = 1
        for i in range(1000):
            if i not in idxmap:
                first_free = i
                break
        if first_free is None:
            raise Exception('Could not find free configuration entry!')
        return first_free

    def GetConfigList(self, new=False):
        '''
        Returns list of available configurations as tuple of (details, verbose).
        '''
        lst = []
        if new:
            lst.append({
                'Id': self.FirstFree(),
                'Path': None,
                'Name': _('Create new configuration')
                })
        lst += self.list

        choices = []
        for config in lst:
            # l10n: %(name)s is name of current configuration or 'Create new
            # configuration', %(position) d is position of this config in .gammurc
            choices.append(
                _('%(name)s (position %(position)d)') % {
                    'name': config['Name'], 'position': config['Id']
                }
            )
        return lst, choices

    def SelectConfig(self, parent=None, force=False, new=False):
        '''
        Shows dialog (if needed) to select configuration.
        '''
        lst, choices = self.GetConfigList(new=new)

        if len(choices) == 1 and not force:
            return lst[0]['Id']

        dlg = wx.SingleChoiceDialog(
            parent,
            _('Select which configration you want to modify.'),
            _('Select configuration section'),
            choices
        )
        if dlg.ShowModal() == wx.ID_OK:
            return lst[dlg.GetSelection()]['Id']
        else:
            return None
