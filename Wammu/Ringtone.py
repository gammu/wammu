# Wammu - Phone manager
# Copyright (c) 2003 - 2004 Michal Cihar 
#
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 2 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for
# more details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc., 59 Temple
# Place, Suite 330, Boston, MA 02111-1307 USA
'''
Ringtone displaying and playing
'''

import wx
import Wammu.Data
import gammu
import os
import thread
import commands
from Wammu.Utils import Str_ as _

ringtones = {}

class Ringtone(wx.BitmapButton):
    def __init__(self, parent, tooltip = 'Melody', ringno = 0, size = None, scale = 1):
        bitmap = wx.BitmapFromXPMData(Wammu.Data.Note)
        wx.BitmapButton.__init__(self, parent, -1, bitmap, (0,0))
        self.SetToolTipString(tooltip)
        self.ringtone = ringtones[int(ringno)]
        wx.EVT_BUTTON(self, self.GetId(), self.OnClick)
 
    def OnClick(self, evt):
        if commands.getstatusoutput('which timidity')[0] != 0:
            wx.MessageDialog(self, 
                _('Could not find timidity, melody can not be played'),
                _('Timidity not found'),
                wx.OK | wx.ICON_ERROR).ShowModal()
            return
        f = os.popen('timidity -', 'w')
        thread.start_new_thread(gammu.SaveRingtone, (f, self.ringtone, "mid"))
