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

