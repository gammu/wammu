import wx
import Wammu.Data
import gammu
import os
import thread
import commands

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
