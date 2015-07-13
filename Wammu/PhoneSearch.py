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
Searching for phone
'''

import wx
import threading
import sys
import Wammu
if Wammu.gammu_error is None:
    import gammu
import Wammu.Data
import Wammu.Events
import wx.lib.layoutf
from Wammu.Locales import StrConv
from Wammu.Locales import ugettext as _
import Wammu.Utils

try:
    import bluetooth
    import Wammu.BluezDiscovery
    BLUETOOTH = 'bluez'
except ImportError:
    BLUETOOTH = None

class AllSearchThread(threading.Thread):
    '''
    Root thread for phone searching. It spawns other threads for testing each
    device.
    '''
    def __init__(self, lock=False, level='nothing', msgcallback=None,
                 callback=None, win=None, noticecallback=None, limit=None):
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
        self.limit = limit

    def create_search_thread(self, device, connections, name):
        '''
        Creates single thread for searching phone on device using listed
        connections. Name is just text which will be shown to user.
        '''
        newthread = SearchThread(
                device,
                connections,
                self.list,
                self.listlock,
                self.lock,
                self.level)
        newthread.setName(name)
        if self.msgcallback is not None:
            self.msgcallback(
                    _('Checking %s') %
                    StrConv(name)
                    )
        self.threads.append(newthread)
        newthread.start()

    def search_bt_device(self, address, name):
        '''
        Searches single Bluetooth device.
        '''
        connections = Wammu.Data.Conn_Bluetooth_All
        vendorguess = _('Could not guess vendor')
        # Use better connection list for some known manufacturers
        for vendor in Wammu.Data.MAC_Prefixes.keys():
            if address[:8].upper() in Wammu.Data.MAC_Prefixes[vendor]:
                connections = Wammu.Data.Conn_Bluetooth[vendor]
                vendorguess = _('Guessed as %s') % vendor

        self.create_search_thread(
                address,
                connections,
                '%s (%s) - %s - %s' % (
                    address,
                    name,
                    vendorguess,
                    str(connections)))

    def check_device(self, curdev):
        '''
        Checks whether it makes sense to perform searching on this device and
        possibly warns user about misconfigurations.
        '''
        res = Wammu.Utils.CheckDeviceNode(curdev)

        if res[0] == 0:
            return True
        if res[0] == -1:
            return False
        if res[1] != '' and self.msgcallback is not None:
            self.msgcallback(res[1])
        if res[2] != '' and self.noticecallback is not None:
            self.noticecallback(res[2], res[3])
        return False

    def search_device(self, curdev, dev):
        '''
        Performs search on one real device.
        '''
        if len(curdev) > 0 and curdev[0] == '/':
            if not self.check_device(curdev):
                return

        self.create_search_thread(
                curdev,
                dev[0],
                '%s - %s' % (curdev, str(dev[0])))

    def listed_device_search(self):
        '''
        Initiates searching of devices defined in Wammu.Data.AllDevices.
        '''
        for dev in Wammu.Data.AllDevices:
            if self.limit != 'all' and self.limit not in dev[3]:
                continue
            if dev[1].find('%d') >= 0:
                for i in range(*dev[2]):
                    curdev = dev[1] % i
                    self.search_device(curdev, dev)
            else:
                self.search_device(dev[1], dev)

    def bluetooth_device_search_bluez(self):
        '''
        Initiates searching for Bluetooth devices using PyBluez stack.
        '''
        # read devices list
        if self.msgcallback is not None:
            self.msgcallback(
                _('Discovering Bluetooth devices using %s') % 'PyBluez'
            )

        try:
            discovery = Wammu.BluezDiscovery.Discovery(self)
            discovery.find_devices()
            discovery.process_inquiry()
            if len(discovery.names_found) == 0 and self.msgcallback is not None:
                self.msgcallback(_('No Bluetooth device found'))
            if self.msgcallback is not None:
                self.msgcallback(_('All Bluetooth devices discovered, connection tests still in progress...'))
        except bluetooth.BluetoothError, txt:
            if self.msgcallback is not None:
                self.msgcallback(
                        _('Could not access Bluetooth subsystem (%s)') %
                        StrConv(txt))

    def bluetooth_device_search(self):
        '''
        Initiates searching for Bluetooth devices.
        '''
        if self.limit not in ['all', 'bluetooth']:
            return
        if BLUETOOTH == 'bluez':
            self.bluetooth_device_search_bluez()
        else:
            if self.msgcallback is not None:
                self.msgcallback(_('PyBluez not found, it is not possible to scan for Bluetooth devices.'))
            if self.noticecallback is not None:
                self.noticecallback(
                        _('No Bluetooth searching'),
                        _('PyBluez not found, it is not possible to scan for Bluetooth devices.'))

    def run(self):
        try:
            self.listed_device_search()
            self.bluetooth_device_search()

            i = 0
            while len(self.threads) > 0:
                if self.threads[i].isAlive():
                    i += 1
                else:
                    if self.msgcallback is not None:
                        self.msgcallback(
                            _('Finished %s') % StrConv(self.threads[i].getName())
                        )
                    del self.threads[i]
                if i >= len(self.threads):
                    i = 0
            if self.msgcallback is not None:
                self.msgcallback(
                    _('All finished, found %d phones') % len(self.list)
                )
            if self.callback is not None:
                self.callback(self.list)
        except:
            evt = Wammu.Events.ExceptionEvent(data=sys.exc_info())
            wx.PostEvent(self.win, evt)

class SearchThread(threading.Thread):
    def __init__(self, device, connections, lst, listlock, lock=False,
                 level='nothing', win=None):
        threading.Thread.__init__(self)
        self.device = device
        self.connections = connections
        self.lock = lock
        self.win = win
        self.level = level
        self.list = lst
        self.listlock = listlock

    def try_connection(self, connection):
        '''
        Performs test on single connection.
        '''
        gsm = gammu.StateMachine()
        cfg = {
            'StartInfo': False,
            'UseGlobalDebugFile': True,
            'DebugFile': '',
            'SyncTime': False,
            'Connection': connection,
            'LockDevice': self.lock,
            'DebugLevel': self.level,
            'Device': self.device,
            'Model': ''
        }

        # Compatibility with old Gammu versions
        cfg = Wammu.Utils.CompatConfig(cfg)

        gsm.SetConfig(0, cfg)

        # Compatibility with old Gammu versions
        cfg = Wammu.Utils.CompatConfig(cfg)

        try:
            if self.level == 'textall':
                print 'Trying at %s using %s' % (self.device, connection)
            gsm.Init()
            self.listlock.acquire()
            self.list.append((
                self.device,
                connection,
                gsm.GetModel(),
                gsm.GetManufacturer()
                ))
            self.listlock.release()
            if self.level != 'nothing':
                print '!!Found model %s at %s using %s' % (
                        gsm.GetModel(),
                        self.device,
                        connection)
            return
        except gammu.GSMError:
            if self.level == 'textall':
                print 'Failed at %s using %s' % (self.device, connection)

    def run(self):
        '''
        Tests all listed connections.
        '''
        try:
            for conn in self.connections:
                self.try_connection(conn)
        except:
            evt = Wammu.Events.ExceptionEvent(data=sys.exc_info())
            wx.PostEvent(self.win, evt)

class PhoneInfoThread(threading.Thread):
    def __init__(self, win, device, connection):
        threading.Thread.__init__(self)
        self.device = device
        self.connection = connection
        self.result = None
        self.win = win

    def run(self):
        if self.connection.lower().find('blue') == -1 and self.connection.lower().find('irda') == -1:
            res = Wammu.Utils.CheckDeviceNode(self.device)
            if res[0] != 0:
                evt = Wammu.Events.DataEvent(
                        data=None,
                        error=(res[2], res[3]))
                wx.PostEvent(self.win, evt)
                return
        try:
            sm = gammu.StateMachine()
            cfg = {
                'StartInfo': False,
                'UseGlobalDebugFile': True,
                'DebugFile': '',
                'SyncTime': False,
                'Connection': self.connection,
                'LockDevice': False,
                'DebugLevel': 'nothing',
                'Device': self.device,
                'Model': '',
            }

            # Compatibility with old Gammu versions
            cfg = Wammu.Utils.CompatConfig(cfg)

            sm.SetConfig(0, cfg)
            sm.Init()
            self.result = {
                    'Model': sm.GetModel(),
                    'Manufacturer': sm.GetManufacturer(),
                    }
            evt = Wammu.Events.DataEvent(data=self.result)
            wx.PostEvent(self.win, evt)
        except gammu.GSMError, val:
            info = val.args[0]
            evt = Wammu.Events.DataEvent(
                data=None,
                error=(
                    _('Failed to connect to phone'),
                    Wammu.Utils.FormatError('', info)
                )
            )
            wx.PostEvent(self.win, evt)
