# Wammu - Phone manager
# Copyright (c) 2003-4 Michal Cihar 
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
Logging window and thread for log reading
'''

import threading
import wx
import Wammu.Events

class Logger(threading.Thread):
    def __init__(self, win, file):
        threading.Thread.__init__(self)
        self.win = win
        self.file = file
        self.canceled = False

    def run(self):
        while not self.canceled:
            txt = self.file.readline()
            evt = Wammu.Events.LogEvent(txt = txt)
            wx.PostEvent(self.win, evt)

class LogFrame(wx.Frame):
    def __init__(self, parent, cfg):
        self.cfg = cfg
        if cfg.HasEntry('/Debug/X') and cfg.HasEntry('/Debug/Y'):
            pos = wx.Point(cfg.ReadInt('/Debug/X', 0), cfg.ReadInt('/Debug/Y', 0))
        else:
            pos =wx.DefaultPosition
        size = wx.Size(cfg.ReadInt('/Debug/Width', 400), cfg.ReadInt('/Debug/Height', 200))
        wx.Frame.__init__(self, parent, -1, 'Wammu debug log', pos, size, wx.DEFAULT_FRAME_STYLE | wx.RESIZE_BORDER)
        self.txt = wx.TextCtrl(self,-1, 'Here will appear debug messages from Gammu...\n',style = wx.TE_MULTILINE | wx.TE_READONLY)
        self.txt.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.NORMAL))
        Wammu.Events.EVT_LOG(self, self.OnLog)
        wx.EVT_SIZE(self, self.OnSize)
        self.OnSize(None)
        
    def OnLog(self, evt):
        self.txt.AppendText(evt.txt)
        
    def OnSize(self, evt):
        w,h = self.GetClientSizeTuple()
        self.txt.SetDimensions(0, 0, w, h)
