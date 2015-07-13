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
HTML displayer with custom link handling
'''

import wx
import wx.html
import Wammu.Events
import Wammu.Utils
from Wammu.Locales import StrConv


class Displayer(wx.html.HtmlWindow):
    def __init__(self, parent, win):
        wx.html.HtmlWindow.__init__(self, parent, -1)
        self.win = win

    def SetContent(self, text):
        # default system colours
        bgc = wx.SystemSettings.GetColour(wx.SYS_COLOUR_LISTBOX)
        fgc = wx.SystemSettings.GetColour(wx.SYS_COLOUR_WINDOWTEXT)
        hfgc = wx.SystemSettings.GetColour(wx.SYS_COLOUR_WINDOWTEXT)

        colours = 'text="#%02x%02x%02x" bgcolor="#%02x%02x%02x" link="#%02x%02x%02x"' % (
            fgc.Red(), fgc.Green(), fgc.Blue(),
            bgc.Red(), bgc.Green(), bgc.Blue(),
            hfgc.Red(), hfgc.Green(), hfgc.Blue())

        pagefmt = u'<html><head><meta http-equiv="Content-Type" content="text/html; charset=%s"></head><body %s>%s</body></html>'

        charset = 'ucs-2'
        text = StrConv(text)
        self.SetPage(pagefmt % (charset, colours, text))


    def OnLinkClicked(self, linkinfo):
        evt = Wammu.Events.LinkEvent(
            link=linkinfo.GetHref()
        )
        wx.PostEvent(self.win, evt)
