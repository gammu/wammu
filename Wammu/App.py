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
Main Wammu application
'''

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

        self.SetAppName('Wammu')
        vendor = StrConv(u'Michal Čihař')
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
        print _('Failed to set exception handler.')
    app = WammuApp()
    app.MainLoop()
