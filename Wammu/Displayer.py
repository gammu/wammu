# Wammu - Phone manager
# Copyright (c) 2003-4 Michal Cihar 
#
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 2 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MER- CHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for
# more details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc., 59 Temple
# Place, Suite 330, Boston, MA 02111-1307 USA

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

        
