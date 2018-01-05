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
#
'''
Wammu - Phone manager
Main Wammu application
'''
from __future__ import unicode_literals
from __future__ import print_function

import wx
import sys
import Wammu.Main
import Wammu.Error
from Wammu.Locales import StrConv
from Wammu.Locales import ugettext as _


class WammuApp(wx.App):
    '''
    Wammu appliction class, it initializes wx and creates main Wammu window.
    '''

    def OnInit(self):
        '''
        wxWindows call this method to initialize the application.
        '''

        self.locale = wx.Locale(wx.LANGUAGE_DEFAULT)
        self.SetAppName('Wammu')
        vendor = StrConv('Michal Čihař')
        if vendor.find('?') != -1:
            vendor = 'Michal Čihař'
        self.SetVendorName(vendor)

        frame = Wammu.Main.WammuFrame(None, -1)
        Wammu.Error.HANDLER_PARENT = frame

        frame.Show(True)
        frame.PostInit(self)
        self.SetTopWindow(frame)

        # Return a success flag
        return True

def Run():
    '''
    Wrapper to execute Wammu. Installs graphical error handler and launches
    WammuApp.
    '''
    try:
        sys.excepthook = Wammu.Error.Handler
    except:
        print(_('Failed to set exception handler.'))
    app = WammuApp()
    app.MainLoop()
