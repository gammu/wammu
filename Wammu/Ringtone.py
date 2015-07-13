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
Ringtone displaying and playback
'''

import wx
import Wammu.Data
import Wammu
if Wammu.gammu_error is None:
    import gammu
import os
import thread
import commands
from Wammu.Locales import ugettext as _

ringtones = {}

class Ringtone(wx.BitmapButton):
    def __init__(self, parent, tooltip='Melody', ringno=0, size=None, scale=1):
        bitmap = wx.BitmapFromXPMData(Wammu.Data.Note)
        wx.BitmapButton.__init__(self, parent, -1, bitmap, (0, 0))
        self.SetToolTipString(tooltip)
        self.ringtone = ringtones[int(ringno)]
        wx.EVT_BUTTON(self, self.GetId(), self.OnClick)

    def OnClick(self, evt):
        if commands.getstatusoutput('which timidity')[0] != 0:
            wx.MessageDialog(
                self,
                _('Could not find timidity, melody can not be played'),
                _('Timidity not found'),
                wx.OK | wx.ICON_ERROR
            ).ShowModal()
            return
        f = os.popen('timidity -', 'w')
        thread.start_new_thread(gammu.SaveRingtone, (f, self.ringtone, "mid"))
