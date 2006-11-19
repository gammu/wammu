# -*- coding: UTF-8 -*-
'''
Wammu - Phone manager
Phone configuration wizard
'''
__author__ = 'Michal Čihař'
__email__ = 'michal@cihar.com'
__license__ = '''
Copyright (c) 2003 - 2006 Michal Čihař

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
import wx.wizard
import Wammu.Paths
from Wammu.Utils import StrConv, Str_ as _


class TitlePage(wx.wizard.WizardPageSimple):
    def __init__(self, parent, titletext, bodytext):
        wx.wizard.WizardPageSimple.__init__(self, parent)
        sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(sizer)
        title = wx.StaticText(self, -1, titletext)
        title.SetFont(wx.Font(18, wx.SWISS, wx.NORMAL, wx.BOLD))
        sizer.Add(title, 0, wx.ALIGN_CENTRE|wx.ALL, 5)
        sizer.Add(wx.StaticLine(self, -1), 0, wx.EXPAND|wx.ALL, 5)
        body = wx.StaticText(self, -1, bodytext)
        body.Wrap(400)
        sizer.Add(body, 0, wx.ALL, 5)

def RunConfigureWizard(parent):
    """
    Executes wizard for configuring phone
    """
    bmp = wx.Bitmap(Wammu.Paths.MiscPath('phonewizard'))
    wiz = wx.wizard.Wizard(parent, -1, _('Wammu Phone Configuration Wizard'), bmp)
    title = TitlePage(wiz, _('Welcome'), _('This wizard will help you with configuring phone connection in Wammu.'))
    wiz.FitToPage(title)
    if wiz.RunWizard(title):
        return "Configured"
    else:
        return None

class WizardApp(wx.App):
    def OnInit(self):

        self.SetAppName('Wammu Phone Configuration Wizard')
        vendor = StrConv(u'Michal Čihař')
        if vendor.find('?') != -1:
            vendor = 'Michal Čihař'
        self.SetVendorName(vendor)

        wx.InitAllImageHandlers()

        # Return a success flag
        return True

if __name__ == '__main__':
    import gettext
    gettext.install('wammu', unicode=1)
    app = WizardApp()
    print RunConfigureWizard(None)
    app.Destroy()
