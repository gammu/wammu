# -*- coding: UTF-8 -*-
# Wammu - Phone manager
# Copyright (c) 2003 - 2006 Michal Čihař
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
'''
HTML displayer with custom link handling
'''

import wx.html
import Wammu.Events

class Displayer(wx.html.HtmlWindow):
    def __init__(self, parent, win):
        wx.html.HtmlWindow.__init__(self, parent, -1)
        self.win = win

    def OnLinkClicked(self, linkinfo):
        evt = Wammu.Events.LinkEvent(
            link = linkinfo.GetHref()
            )
        wx.PostEvent(self.win, evt)


