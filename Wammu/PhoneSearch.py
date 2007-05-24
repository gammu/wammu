# -*- coding: UTF-8 -*-
# vim: expandtab sw=4 ts=4 sts=4:
'''
Wammu - Phone manager
Searching for phone
'''
__author__ = 'Michal Čihař'
__email__ = 'michal@cihar.com'
__license__ = '''
Copyright (c) 2003 - 2007 Michal Čihař

This program is free software; you can redistribute it and/or modify it
under the terms of the GNU General Public License version 2 as published by
the Free Software Foundation.

This program is distributed in the hope that it will be useful, but WITHOUT
ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for
more details.

You should have received a copy of the GNU General Public License along with
this program; if not, write to the Free Software Foundation, Inc.,
51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
'''

import wx
import threading
import os
import os.path
import sys
try:
    import grp
except ImportError:
    pass
import Wammu
if Wammu.gammu_error == None:
    import gammu
import Wammu.Data
import Wammu.Events
import wx.lib.layoutf
from Wammu.Locales import StrConv

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
        text.SetConstraints(wx.lib.layoutf.Layoutf('t=t5#1;b=t5#2;l=l5#1;r=r5#1', (self,ok)))
        ok.SetConstraints(wx.lib.layoutf.Layoutf('b=b5#1;x%w50#1;w!80;h!25', (self,)))
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
        self.text.AppendText(StrConv(evt.text))

    def OnDone(self, evt):
        self.ok.Enable(True)
        self.canclose = True


class AllSearchThread(threading.Thread):
    def __init__(self, lock = 'no', level = 'nothing', msgcallback = None, callback = None, win = None, noticecallback = None):
        threading.Thread.__init__(self)
        self.lock = lock
        self.list = []
        self.win = win
        self.listlock = threading.Lock()
        self.level = level
        self.threads = []
        self.callback = callback
        self.msgcallback = msgcallback
        self.noticecallback = noticecallback

    def run(self):
        try:
            for dev in Wammu.Data.AllDevices:
                if dev[1].find('%d') >= 0:
                    for i in range(*dev[2]):
                        curdev = dev[1] % i
                        if curdev[0] == '/':
                            if not os.path.exists(curdev):
                                continue
                            if not os.access(curdev, os.R_OK) or not os.access(curdev, os.W_OK):
                                gid =  os.stat(curdev).st_gid
                                try:
                                    group = grp.getgrgid(gid)[0]
                                except NameError:
                                    group = str(gid)
                                if self.msgcallback != None:
                                    self.msgcallback(_('You don\'t have permissions for %s device!') % curdev)
                                if self.noticecallback != None:
                                    self.noticecallback(
                                            _('Error opening device'), 
                                            (_('You don\'t have permissions for %s device!') % curdev) + ' ' +
                                            (_('Maybe you need to be member of %s group.') % group))

                        t = SearchThread(curdev, dev[0], self.list, self.listlock, self.lock, self.level, self.win)
                        t.setName('%s - %s' % (curdev, str(dev[0])))
                        if self.msgcallback != None:
                            self.msgcallback(_('Starting %s') %  t.getName())
                        self.threads.append(t)
                        t.start()
                else:
                    # need to handle devices without name here
                    if len(dev[1]) > 0 and dev[1][0] == '/' and not os.path.exists(dev[1]):
                        continue
                    t = SearchThread(dev[1], dev[0], self.list, self.listlock, self.lock, self.level)
                    t.setName('%s - %s' % (dev[1], ', '.join(dev[0])))
                    self.threads.append(t)
                    t.start()

            try:
                import bluetooth
                devs = []
                # read devices list
                if self.msgcallback != None:
                    self.msgcallback(_('Scanning for bluetooth devices using %s') % 'PyBluez')

                try:
                    nearby_devices = bluetooth.discover_devices()

                    if len(nearby_devices) == 0 and self.msgcallback != None:
                        self.msgcallback(_('No bluetooth device found'))

                    for bdaddr in nearby_devices:
                        t = SearchThread(bdaddr, Wammu.Data.Conn_Bluetooth, self.list, self.listlock, self.lock, self.level)
                        t.setName('%s (%s) - %s' % (bdaddr, bluetooth.lookup_name(bdaddr), Wammu.Data.Conn_Bluetooth))
                        if self.msgcallback != None:
                            self.msgcallback(_('Checking %s') %  StrConv(t.getName()))
                        self.threads.append(t)
                        t.start()
                    if self.msgcallback != None:
                        self.msgcallback(_('Bluetooth device scan completed'))
                except bluetooth.BluetoothError, txt:
                    if self.msgcallback != None:
                        self.msgcallback(_('Could not access Bluetooth subsystem (%s)') % StrConv(txt))
            except ImportError:
                try:
                    import btctl
                    # create controller object
                    try:
                        ctl = btctl.Controller('')
                    except TypeError:
                        ctl = btctl.Controller()
                    # read devices list
                    if self.msgcallback != None:
                        self.msgcallback(_('Scanning for bluetooth devices using %s') % 'GNOME Bluetooth')

                    devs = ctl.discover_devices()

                    if devs == None or len(devs) == 0:
                        if self.msgcallback != None:
                            self.msgcallback(_('No bluetooth device found'))
                    else:
                        for dev in devs:
                            t = SearchThread(dev['bdaddr'], Wammu.Data.Conn_Bluetooth, self.list, self.listlock, self.lock, self.level)
                            t.setName('%s (%s) - %s' % (dev['bdaddr'], ctl.get_device_preferred_name(dev['bdaddr']), Wammu.Data.Conn_Bluetooth))
                            if self.msgcallback != None:
                                self.msgcallback(_('Checking %s') %  t.getName())
                            self.threads.append(t)
                            t.start()
                    if self.msgcallback != None:
                        self.msgcallback(_('Bluetooth device scan completed'))
                except ImportError:
                    if self.msgcallback != None:
                        self.msgcallback(_('Neither GNOME Bluetooth nor PyBluez found, not possible to scan for bluetooth devices'))
                    if self.noticecallback != None:
                        self.noticecallback(
                                _('No bluetooth searching'), 
                                _('Neither GNOME Bluetooth nor PyBluez found, not possible to scan for bluetooth devices'))

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
        except:
            evt = Wammu.Events.ExceptionEvent(data = sys.exc_info())
            wx.PostEvent(self.win, evt)

class SearchThread(threading.Thread):
    def __init__(self, device, connections, lst, listlock, lock = 'no', level = 'nothing', win = None):
        threading.Thread.__init__(self)
        self.device = device
        self.connections = connections
        self.lock = lock
        self.win = win
        self.level = level
        self.list = lst
        self.listlock = listlock

    def run(self):
        try:
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
        except:
            evt = Wammu.Events.ExceptionEvent(data = sys.exc_info())
            wx.PostEvent(self.win, evt)

class PhoneInfoThread(threading.Thread):
    def __init__(self, win, device, connection):
        threading.Thread.__init__(self)
        self.device = device
        self.connection = connection
        self.result = None
        self.win = win

    def run(self):
        try:
            sm = gammu.StateMachine()
            sm.SetConfig(0,
                    {'StartInfo': 'no',
                     'UseGlobalDebugFile': 1,
                     'DebugFile': '',
                     'SyncTime': 'no',
                     'Connection': self.connection,
                     'LockDevice': 'no',
                     'DebugLevel': 'nothing',
                     'Device': self.device,
                     'Localize': None,
                     'Model': ''})
            sm.Init()
            self.result = {'Model': sm.GetModel(), 'Manufacturer': sm.GetManufacturer()}
            evt = Wammu.Events.DataEvent(data = self.result)
            wx.PostEvent(self.win, evt)
        except gammu.GSMError:
            evt = Wammu.Events.DataEvent(data = None)
            wx.PostEvent(self.win, evt)
