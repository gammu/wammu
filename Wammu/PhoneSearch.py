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
Searching for phone
'''

import wx
import gammu
import threading
import Wammu
import Wammu.Data
import Wammu.Events
import wxPython.lib.layoutf
from Wammu.Utils import Str_ as _

class LogDialog(wx.Dialog):
    def __init__(self, parent, msg = '', caption = _('Phone searching log'), pos = wx.DefaultPosition, size = (500,300)):
        wx.Dialog.__init__(self, parent, -1, caption, pos, size)
        x, y = pos
        if x == -1 and y == -1:
            self.CenterOnScreen(wx.BOTH)
        text = wx.TextCtrl(self, -1, msg, wx.DefaultPosition,
                             wx.DefaultSize,
                             wx.TE_MULTILINE | wx.TE_READONLY)
        ok = wx.Button(self, wx.ID_OK, _('Close'))
        text.SetConstraints(wxPython.lib.layoutf.Layoutf('t=t5#1;b=t5#2;l=l5#1;r=r5#1', (self,ok)))
        ok.SetConstraints(wxPython.lib.layoutf.Layoutf('b=b5#1;x%w50#1;w!80;h!25', (self,)))
        self.SetAutoLayout(1)
        self.Layout()
        self.text = text
        self.ok = ok
        self.ok.Enable(False)
        Wammu.Events.EVT_TEXT(self, self.OnText)
        Wammu.Events.EVT_DONE(self, self.OnDone)
        wx.EVT_CLOSE(self, self.CloseWindow)
        self.canclose = False

    def CloseWindow(self, event):
        if self.canclose:
            self.EndModal(wx.ID_CANCEL)
        
    def OnText(self, evt):
        self.text.AppendText(evt.text)

    def OnDone(self, evt):
        self.ok.Enable(True)
        self.canclose = True
        
        
class AllSearchThread(threading.Thread):
    def __init__(self, lock = 'no', level = 'nothing', msgcallback = None, callback = None):
        threading.Thread.__init__(self)
        self.lock = lock
        self.list = []
        self.listlock = threading.Lock()
        self.level = level
        self.threads = []
        self.callback = callback
        self.msgcallback = msgcallback

    def run(self):
        for dev in Wammu.Data.AllDevices:
            if dev[1].find('%d') >= 0:
                for i in range(*dev[2]):
                    curdev = dev[1] % i
                    t = SearchThread(curdev, dev[0], self.list, self.listlock, self.lock, self.level)
                    t.setName('%s - %s' % (curdev, str(dev[0])))
                    if self.msgcallback != None:
                        self.msgcallback(_('Starting %s') %  t.getName())
                    self.threads.append(t)
                    t.start()
            else:
                t = SearchThread(dev[1], dev[0], self.list, self.listlock, self.lock, self.level)
                t.setName('%s - %s' % (dev[1], ', '.join(dev[0])))
                self.threads.append(t)
                t.start()
        i = 0
        while len(self.threads) > 0:
            if self.threads[i].isAlive():
                i += 1
            else:
                if self.msgcallback != None:
                    self.msgcallback(_('Finished %s') % self.threads[i].getName())
                del self.threads[i]
            if i >= len(self.threads):
                i = 0
        if self.msgcallback != None:
            self.msgcallback(_('All finished, found %d phones') % len(self.list))
        if self.callback != None:
            self.callback(self.list)

class SearchThread(threading.Thread):
    def __init__(self, device, connections, lst, listlock, lock = 'no', level = 'nothing'):
        threading.Thread.__init__(self)
        self.device = device
        self.connections = connections
        self.lock = lock
        self.level = level
        self.list = lst
        self.listlock = listlock

    def run(self):
        sm = gammu.StateMachine()
        for conn in self.connections:
            sm.SetConfig(0,
                    {'StartInfo': 'no',
                     'UseGlobalDebugFile': 1, 
                     'DebugFile': '', 
                     'SyncTime': 'no', 
                     'Connection': conn, 
                     'LockDevice': self.lock, 
                     'DebugLevel': self.level, 
                     'Device': self.device, 
                     'Localize': None, 
                     'Model': ''})
            try:
                if self.level == 'textall':
                    print 'Trying at %s using %s' % (self.device, conn)
                sm.Init()
                self.listlock.acquire()
                self.list.append((self.device, conn, sm.GetModel(), sm.GetManufacturer()))
                self.listlock.release()
                if self.level != 'nothing':
                    print '!!Found model %s at %s using %s' % (sm.GetModel(), self.device, conn)
                return
            except gammu.GSMError:
                if self.level == 'textall':
                    print 'Failed at %s using %s' % (self.device, conn)
                pass
