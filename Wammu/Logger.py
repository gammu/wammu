import threading
import time
import wx
import os
import Wammu.Events

class Logger(threading.Thread):
    def __init__(self, win, file):
        threading.Thread.__init__(self)
        self.win = win
        self.file = file
        self.canceled = False

    def run(self):
        while not self.canceled:
            print 'P:read'
#            txt = self.file.readline()
#            print 'P:got ' + txt
#            evt = Wammu.Events.LogEvent(txt = txt)
#            wx.PostEvent(self.win, evt)

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
