import threading
import wx
import Wammu.Events

class Thread(threading.Thread):
    def __init__(self, win, sm):
        threading.Thread.__init__(self)
        self.win = win
        self.sm = sm
        self.canceled = False

    def Cancel(self):
        self.canceled = True
        
    def ShowError(self, info, finish = False):
        if finish:
            self.ShowProgress(100)
        lck = threading.Lock()
        lck.acquire()
        evt = Wammu.Events.ShowMessageEvent(
            message = 'Got error from phone:\n%s\nIn:%s\nError code: %d' % (info['Text'], info['Where'], info['Code']),
            title = 'Error Occured',
            type = wx.ICON_ERROR,
            lock = lck)
        wx.PostEvent(self.win, evt)
        lck.acquire()

    def ShowMessage(self, title, text):
        lck = threading.Lock()
        lck.acquire()
        evt = Wammu.Events.ShowMessageEvent(
            message = text,
            title = title,
            type = wx.ICON_INFORMATION,
            lock = lck)
        wx.PostEvent(self.win, evt)
        lck.acquire()

    def ShowProgress(self, progress):
        evt = Wammu.Events.ProgressEvent(
            progress = progress,
            cancel = self.Cancel)
        wx.PostEvent(self.win, evt)

    def SendData(self, type, data, last = True):
        evt = Wammu.Events.DataEvent(
            type = type,
            data = data,
            last = last)
        wx.PostEvent(self.win, evt)

    def Canceled(self):
        lck = threading.Lock()
        lck.acquire()
        evt = Wammu.Events.ShowMessageEvent(
            message = 'Action canceled by user!',
            title = 'Action canceled',
            type = wx.ICON_WARNING,
            lock = lck)
        wx.PostEvent(self.win, evt)
        lck.acquire()
        self.ShowProgress(100)

