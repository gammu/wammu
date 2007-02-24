# -*- coding: UTF-8 -*-
# vim: expandtab sw=4 ts=4 sts=4:
'''
Wammu - Phone manager
Error messages
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

import wx
import os
import Wammu
import webbrowser
import Wammu.Paths
import Wammu.ErrorLog


BUG_SEARCH_URL = 'http://bugs.cihar.com/view_all_set.php?f=3&type=1&search=%s'
BUG_REPORT_URL = 'http://bugs.cihar.com/bug_report_page.php?project_id=1'

class ErrorMessage(wx.Dialog):
    '''
    Error message box with support for saving debug log and reporting
    bug to http://bugs.cihar.com/.
    '''
    def __init__(self, parent, message, title, traceid=None,
            autolog=None, exception=None):
        wx.Dialog.__init__(self, parent, -1, title)

        sizer = wx.BoxSizer(wx.VERTICAL)
        textsizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(textsizer, flag=wx.ALL, border=10)

        bitmap = wx.Bitmap(Wammu.Paths.MiscPath('error'))
        icon = wx.StaticBitmap(self, -1, bitmap,
                size = (bitmap.GetWidth(), bitmap.GetHeight()))
        textsizer.Add(icon, flag=wx.RIGHT, border=10)

        if exception is not None:
            message += '\n\n'
            message += exception
        if autolog is not None:
            message += '\n\n'
            message += _('Debug log has been automatically saved to %s, you are strongly encouraged to include it in bugreport.'
                    ) % autolog
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
        sizer.Add(buttonsizer, flag=wx.ALL, border=10)

        sizer.Fit(self)
        self.SetAutoLayout(True)
        self.SetSizer(sizer)

    def OnSave(self, evt):
        '''
        Saves debug log to file.
        '''
        dlg = wx.FileDialog(self,
                _('Save debug log as...'),
                os.getcwd(),
                'wammu.log',
                '',
                wx.SAVE | wx.OVERWRITE_PROMPT | wx.CHANGE_DIR)
        if dlg.ShowModal() == wx.ID_OK:
            Wammu.ErrorLog.SaveLog(filename = dlg.GetPath())

    def OnSearch(self, evt):
        '''
        Opens search for simmilar problems in browser.
        '''
        webbrowser.open(BUG_SEARCH_URL % self.traceid)

    def OnReport(self, evt):
        '''
        Opens web browser with bug reporting page.
        '''
        webbrowser.open(BUG_REPORT_URL)
