import threading
import time
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
            print 'L:' + txt
            if txt == '':
                time.sleep(1)
            else:
                evt = Wammu.Events.LogEvent(txt = txt)
                wx.PostEvent(self.win, evt)
        del self.win
            

class LogFrame(wx.Frame):
    def __init__(self, parent):
        wx.Frame.__init__(self, parent, -1, 'Wammu debug log', wx.DefaultPosition, wx.Size(640,480), wx.DEFAULT_FRAME_STYLE | wx.RESIZE_BORDER)
        self.txt = wx.TextCtrl(self,-1, 'Here will appear debug messages from Gammu...\n', style = wx.TE_MULTILINE | wx.TE_READONLY)
        self.sizer = wx.FlexGridSizer(1, 1, 2, 2)
        self.sizer.AddGrowableCol(1)
        self.sizer.AddGrowableRow(1)
        self.sizer.AddMany([ 
            (self.txt,   0, wx.EXPAND),
            ])
        self.sizer.Fit(self)
        self.SetAutoLayout(True)
        self.SetSizer(self.sizer)
        Wammu.Events.EVT_LOG(self, self.OnLog)
        
    def OnLog(self, evt):
        self.txt.AppendText(evt.txt)
