# -*- coding: UTF-8 -*-
# vim: expandtab sw=4 ts=4 sts=4:
'''
Wammu - Phone manager
Settings storage and configuration manager
'''
__author__ = 'Michal Čihař'
__email__ = 'michal@cihar.com'
__license__ = '''
Copyright (c) 2003 - 2006 Michal Čihař

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

import sys
import Wammu.Paths
import Wammu.Data
from Wammu.Utils import StrConv, Str_ as _

class Settings:
    """
    Helper class for generating settings.
    """
    def __init__(self):
        self.connection = None
        self.driver = None
        self.manufacturer = None
        self.name = None
        self.port = None
        self.gammudriver = None
        self.position = 0

    def GetName(self):
        if self.name is None:
            if self.position == 0:
                return 'gammu'
            else:
                return 'gammu%d', self.position
        else:
            return self.name

    def GetGammuDriver(self):
        return self.gammudriver

    def GetPort(self):
        return self.port

    def SetPosition(self, pos):
        self.position = pos

    def SetConnection(self, conn):
        self.connection = conn

    def SetDriver(self, driver):
        self.driver = driver

    def SetGammuDriver(self, driver):
        self.gammudriver = driver

    def SetManufacturer(self, manu):
        self.manufacturer = manu

    def SetPort(self, port):
        self.port = port

    def SetName(self, name):
        self.name = name

    def GetSettings(self):
        return {'Position': self.position, 'Device': self.port, 'Connection': self.gammudriver, 'Name': self.name}

    def GetManufacturers(self):
        names = []
        connections = []
        helps = []

        names.append('any')
        connections.append(_('I don\'t know'))
        helps.append(_('Select this option only if really necessary. You will be provided with too much options in next step.'))

        names.append('nokia')
        connections.append(_('Nokia phone'))
        helps.append(_('If your phone runs Symbian, please select directly it.'))

        names.append('symbian')
        connections.append(_('Symbian based phone'))
        helps.append(_('Go on if your phone uses Symbian OS (regardless of manufacturer).'))

        names.append('nota')
        connections.append(_('None of the above'))
        helps.append(_('Select this option if nothing above matches, good choice for other manufacturers like Alcatel, BenQ, LG, Sharp, Sony Ericsson...'))

        return (names, connections, helps)

    def GetDrivers(self):
        names = []
        connections = []
        helps = []

        names.append('at')
        connections.append(_('AT based'))
        if self.manufacturer in ['symbian', 'nokia']:
            helps.append(_('This provides minimal access to phone features. It is recommended to use other connection type.'))
        else:
            helps.append(_('Good choice for most phones except Nokia and Symbian based. Provides access to most phone features.'))

        if self.manufacturer in ['nokia', 'any']:
            names.append('fbus')
            connections.append(_('Nokia FBUS'))
            helps.append(_('Nokia proprietary protocol.'))

            if self.connection == 'serial':
                names.append('mbus')
                connections.append(_('Nokia MBUS'))
                helps.append(_('Nokia proprietary protocol. Older version, use FBUS if possible.'))

        names.append('obex')
        connections.append(_('OBEX based'))
        helps.append(_('Standard access to filesystem and sometimes also to phone data. Good choice for recent phones.'))

        if self.manufacturer in ['symbian', 'any']:
            names.append('symbian')
            connections.append(_('Symbian using Gnapplet'))
            helps.append(_('You have to install Gnapplet into phone before using this connection. You can find it in Gammu sources.'))

        return (names, connections, helps)

    def GetPortType(self):
        if self.gammudriver in ['mbus', 'fbus', 'dlr3', 'at', 'at19200', 'at38400', 'at115200', 'obex']:
            if self.connection == 'serial':
                return 'serial'
            elif self.connection == 'bluetooth':
                return 'btserial'
            elif self.connection == 'irda':
                return 'irdaserial'
            elif self.connection == 'usb':
                return 'usbserial'
            return 'serial'
        if self.gammudriver in ['blueat', 'bluerfat', 'blueobex', 'bluerfobex', 'bluerfgnapbus', 'bluerffbus', 'bluephonet', 'bluerfphonet']:
            return 'bluetooth'
        if self.gammudriver in ['dku2', 'dku5', 'dku2at']:
            return 'dku'
        if self.gammudriver in ['irdaat', 'irdaobex', 'irdagnapbus', 'fbusirda', 'irdaphonet']:
            return 'irda'
        # fallback
        return 'serial'

    def GetDevicesWindows(self):
        type = self.GetPortType()
        if type == 'serial':
            return [
                'COM1:',
                'COM2:',
                'COM3:',
                'COM4:',
                'COM5:',
                'COM6:',
                'COM7:',
                'COM8:',
                'COM9:',
                ], _('Enter device name of serial port.')
        elif type in ['btserial', 'irdaserial', 'usbserial']:
            return [
                'COM1:',
                'COM2:',
                'COM3:',
                'COM4:',
                'COM5:',
                'COM6:',
                'COM7:',
                'COM8:',
                'COM9:',
                ], _('Enter device name of emulated serial port.')
        elif type == 'bluetooth':
            # FIXME: scan bluetooth devices here if we have pybluez
            return [], _('Enter Bluetooth address of your phone.')
        elif type in ['irda', 'dku']:
            return [], _('You don\'t have to enter anything for this settings.')

    def GetDevicesUNIX(self):
        type = self.GetPortType()
        if type == 'serial':
            return [
                '/dev/ttyS0',
                '/dev/ttyS1',
                '/dev/ttyS2',
                '/dev/ttyS3',
                '/dev/tts/0',
                '/dev/tts/1',
                '/dev/tts/2',
                '/dev/tts/3',
                ], _('Enter device name of serial port.')
        elif type == 'btserial':
            return [
                '/dev/rfcomm0',
                '/dev/rfcomm1',
                ], _('Enter device name of emulated serial port.')
        elif type == 'irdaserial':
            return [
                '/dev/ircomm0',
                '/dev/ircomm1',
                ], _('Enter device name of emulated serial port.')
        elif type in ['usbserial', 'dku']:
            return [
                '/dev/ttyUSB0',
                '/dev/ttyUSB1',
                '/dev/ttyUSB2',
                '/dev/ttyUSB3',
                '/dev/ttyACM0',
                '/dev/ttyACM1',
                '/dev/ttyACM2',
                '/dev/ttyACM3',
                '/dev/usb/tts/0',
                '/dev/usb/tts/1',
                '/dev/usb/tts/2',
                '/dev/usb/tts/3',
                ], _('Enter device name of USB port.')
        elif type == 'bluetooth':
            # FIXME: scan bluetooth devices here if we have pybluez
            return [], _('Enter Bluetooth address of your phone.')
        elif type == 'irda':
            return [], _('You don\'t have to enter anything for this settings.')


    def GetDevices(self):
        if sys.platform == 'win32':
            return self.GetDevicesWindows()
        else:
            return self.GetDevicesUNIX()

    def GetGammuDrivers(self):
        names = []
        connections = []
        helps = []

        if self.driver == 'at':
            names.append('at')
            connections.append(_('Generic AT over serial line or it\'s emulation'))
            helps.append(_('Select this if you have real serial port or it is emulated by phone driver (eg. virtual COM port, /dev/rfcomm, /dev/ircomm, etc.).'))

            if self.connection == 'serial':
                names.append('at19200')
                connections.append(_('Generic AT at 19200 bps'))
                helps.append(_('Select this if your phone requires transfer speed 19200 bps.'))

                names.append('at38400')
                connections.append(_('Generic AT at 38400 bps'))
                helps.append(_('Select this if your phone requires transfer speed 38400 bps.'))

                names.append('at115200')
                connections.append(_('Generic AT at 115200 bps'))
                helps.append(_('Select this if your phone requires transfer speed 115200 bps.'))

            elif self.connection == 'bluetooth':
                names.append('blueat')
                connections.append(_('AT over Bluetooth'))
                helps.append(_('Select this if your phone is connected over Bluetooth and you want to use native Bluetooth connection.'))

                names.append('bluerfat')
                connections.append(_('AT over Bluetooth with RF searching'))
                helps.append(_('Use for Bluetooth stack and 6210 / DCT4 Nokia models, which don\'t inform about Bluetooth services correctly (6310, 6310i with firmware lower than 5.50, 8910,..)'))

            elif self.connection == 'irda':
                names.append('irdaat')
                connections.append(_('AT over IrDA'))
                helps.append(_('Select this if your phone is connected over IrDA and you want to use native Bluetooth connection.'))

            elif self.manufacturer == 'nokia':
                names.append('dku2at')
                connections.append(_('AT over DKU2'))
                helps.append(_('Select this if your phone is connected using DKU2 cable.'))

        elif self.driver == 'obex':
            names.append('obex')
            connections.append(_('Generic OBEX over serial line or it\'s emulation'))
            helps.append(_('Select this if you have real serial port or it is emulated by phone driver (eg. virtual COM port, /dev/rfcomm, /dev/ircomm, etc.).'))

            if self.connection == 'bluetooth':
                names.append('blueobex')
                connections.append(_('OBEX over Bluetooth'))
                helps.append(_('Select this if your phone is connected over Bluetooth and you want to use native Bluetooth connection.'))

                names.append('bluerfobex')
                connections.append(_('OBEX over Bluetooth with RF searching'))
                helps.append(_('Use for Bluetooth stack and 6210 / DCT4 Nokia models, which don\'t inform about Bluetooth services correctly (6310, 6310i with firmware lower than 5.50, 8910,..)'))

            elif self.connection == 'irda':
                names.append('irdaobex')
                connections.append(_('OBEX over IrDA'))
                helps.append(_('Select this if your phone is connected over IrDA and you want to use native Bluetooth connection.'))

        elif self.driver == 'symbian':
            if self.connection == 'bluetooth':
                names.append('bluerfgnapbus')
                connections.append(_('Gnapplet over Bluetooth'))
                helps.append(_('Select this if your phone is connected over Bluetooth and you want to use native Bluetooth connection.'))

            elif self.connection == 'irda':
                names.append('irdagnapbus')
                connections.append(_('Gnapplet over IrDA'))
                helps.append(_('Select this if your phone is connected over IrDA and you want to use native Bluetooth connection.'))

        elif self.driver == 'mbus':
            if self.connection == 'serial':
                names.append('mbus')
                connections.append(_('MBUS proprietary protocol'))
                helps.append(_('Protocol used in older Nokia phones.'))

        elif self.driver == 'fbus':
            if self.connection == 'serial':
                names.append('fbus')
                connections.append(_('FBUS proprietary protocol'))
                helps.append(_('Protocol used in Nokia phones. Please try selecting more specific options first.'))

                names.append('dlr3')
                connections.append(_('DLR3-3P cable'))
                helps.append(_('Nokia RS-232 Adapter Cable DLR-3P, usually with phones like Nokia 7110/6210/6310/6310.'))

            # Serial should not be here, but we do not trust people they really have serial :-)
            if self.connection in ['serial', 'usb']:
                names.append('fbuspl2303')
                connections.append(_('PL2303 cable'))
                helps.append(_('New Nokia protocol for PL2303 USB cable (for phones with USB chip like 5100).'))

                names.append('dku5')
                connections.append(_('DKU5 cable'))
                helps.append(_('Nokia Connectivity Adapter Cable DKU-5 (for phones with USB chip like 5100).'))

                names.append('dku2')
                connections.append(_('DKU2 cable'))
                helps.append(_('Nokia Connectivity Cable DKU-2 (for phones without USB chip like 6230).'))

            elif self.connection == 'bluetooth':
                names.append('bluerffbus')
                connections.append(_('FBUS over Bluetooth'))
                helps.append(_('Nokia protocol for Bluetooth stack with Nokia 6210'))

                names.append('bluephonet')
                connections.append(_('Phonet over Bluetooth'))
                helps.append(_('Nokia protocol for Bluetooth stack with other DCT4 Nokia models'))

                names.append('bluerfphonet')
                connections.append(_('Phonet over Bluetooth with RF searching'))
                helps.append(_('Nokia protocol for Bluetooth stack with DCT4 Nokia models, which don\'t inform about services correctly (6310, 6310i with firmware lower than 5.50, 8910,..)'))

            elif self.connection == 'irda':
                names.append('fbusirda')
                connections.append(_('FBUS over IrDA'))
                helps.append(_('Nokia protocol for infrared with Nokia 6110/6130/6150'))

                names.append('irdaphonet')
                connections.append(_('Phonet over IrDA'))
                helps.append(_('Nokia protocol for infrared with other Nokia models'))

        return (names, connections, helps)
