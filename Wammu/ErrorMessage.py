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
Error messages
'''

import wx
import os
import Wammu
import Wammu.Webbrowser
import Wammu.Paths
import Wammu.ErrorLog
from Wammu.Locales import ugettext as _


BUG_SEARCH_URL = 'https://github.com/search?l=&q=%s+%%40gammu&ref=advsearch&type=Issues'
BUG_REPORT_URL = 'https://github.com/gammu/wammu/issues/new'

class ErrorMessage(wx.Dialog):
    '''
    Error message box with support for saving debug log and reporting
    bug to https://github.com/gammu/wammu/issues.
    '''
    def __init__(self, parent, message, title, traceid=None,
                 autolog=None, exception=None):
        wx.Dialog.__init__(self, parent, -1, title)

        sizer = wx.BoxSizer(wx.VERTICAL)
        textsizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(textsizer, flag=wx.ALL, border=10)

        bitmap = wx.Bitmap(Wammu.Paths.MiscPath('error'))
        icon = wx.StaticBitmap(
            self, -1, bitmap,
            size=(bitmap.GetWidth(), bitmap.GetHeight())
        )
        textsizer.Add(icon, flag=wx.RIGHT, border=10)

        if exception is not None:
            message += '\n\n'
            message += exception
        if autolog is not None:
            message += '\n\n'
            message += (
                    _('Debug log has been automatically saved to %s, you are strongly encouraged to include it in bugreport.')
                    % autolog)
        msg = wx.StaticText(self, -1, message)
        msg.Wrap(400)
        textsizer.Add(msg)

        buttonsizer = wx.StdDialogButtonSizer()
        buttonsizer.AddButton(wx.Button(self, wx.ID_OK))

        if traceid is None:
            savebutton = wx.Button(self, -1, _('Save debug log...'))
            buttonsizer.SetCancelButton(savebutton)
            self.Bind(wx.EVT_BUTTON, self.OnSave, savebutton)
        else:
            self.traceid = traceid
            searchbutton = wx.Button(self, -1, _('Search for similar reports'))
            buttonsizer.SetCancelButton(searchbutton)
            self.Bind(wx.EVT_BUTTON, self.OnSearch, searchbutton)

        self.reportbutton = wx.Button(self, -1, _('Report bug'))
        buttonsizer.SetNegativeButton(self.reportbutton)
        self.Bind(wx.EVT_BUTTON, self.OnReport, self.reportbutton)

        buttonsizer.Realize()
        sizer.Add(buttonsizer, flag=wx.ALIGN_RIGHT | wx.ALL, border=10)

        sizer.Fit(self)
        self.SetAutoLayout(True)
        self.SetSizer(sizer)

    def OnSave(self, evt):
        '''
        Saves debug log to file.
        '''
        dlg = wx.FileDialog(
            self,
            _('Save debug log as...'),
            os.getcwd(),
            'wammu.log',
            '',
            wx.SAVE | wx.OVERWRITE_PROMPT | wx.CHANGE_DIR
        )
        if dlg.ShowModal() == wx.ID_OK:
            Wammu.ErrorLog.SaveLog(filename=dlg.GetPath())

    def OnSearch(self, evt):
        '''
        Opens search for simmilar problems in browser.
        '''
        Wammu.Webbrowser.Open(BUG_SEARCH_URL % self.traceid)

    def OnReport(self, evt):
        '''
        Opens web browser with bug reporting page.
        '''
        Wammu.Webbrowser.Open(BUG_REPORT_URL)
