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
Settings storage and configuration manager
'''

import sys
import Wammu.Paths
import Wammu.Data
import Wammu.Utils
from Wammu.Locales import ugettext as _

COM_PORTS = 16
UNX_DEVICES = 4


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
                return 'gammu%d' % self.position
        else:
            return self.name

    def GetGammuDriver(self):
        return self.gammudriver

    def GetPort(self):
        return self.port

    def GetConnection(self):
        return self.connection

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

        names.append('symbian')
        connections.append(_('Symbian based phone'))
        helps.append(_('Go on if your phone uses Symbian OS (regardless of manufacturer).'))

        names.append('nota')
        connections.append(_('Alcatel phone'))
        helps.append(_('Alcatel phone not running Symbian.'))

        names.append('nota')
        connections.append(_('BenQ/Siemens phone'))
        helps.append(_('BenQ or Siemens phone not running Symbian.'))

        names.append('nota')
        connections.append(_('Motorola phone'))
        helps.append(_('Motorola phone not running Symbian.'))

        names.append('nokia')
        connections.append(_('Nokia phone'))
        helps.append(_('Nokia phone not running Symbian.'))

        names.append('nota')
        connections.append(_('Samsung phone'))
        helps.append(_('Samsung phone not running Symbian.'))

        names.append('nota')
        connections.append(_('Sharp phone'))
        helps.append(_('Sharp phone not running Symbian.'))

        names.append('nota')
        connections.append(_('Sony Ericsson phone'))
        helps.append(_('Sony Ericsson phone not running Symbian.'))

        names.append('nota')
        connections.append(_('None of the above'))
        helps.append(_('Select this option if nothing above matches.'))

        return (names, connections, helps)

    def AddOBEX(self, names, connections, helps):
        names.append('obex')
        connections.append(_('OBEX and IrMC protocols'))
        if self.manufacturer in ['symbian', 'nokia']:
            helps.append(_('Standard access to filesystem. Not a good choice for Nokia if you want to access data.'))
        else:
            helps.append(_('Standard access to filesystem and sometimes also to phone data. Good choice for recent phones.'))

    def AddSymbian(self, names, connections, helps):
        names.append('symbian')
        connections.append(_('Symbian using Gnapplet'))
        helps.append(_('You have to install Gnapplet into phone before using this connection. You can find it in Gammu sources.'))

    def AddNokia(self, names, connections, helps):
        names.append('fbus')
        connections.append(_('Nokia proprietary protocol'))
        helps.append(_('Nokia proprietary protocol FBUS.'))
        if self.connection == 'serial':
            names.append('mbus')
            connections.append(_('Nokia proprietary service protocol'))
            helps.append(_('Nokia proprietary protocol MBUS. Older version, use FBUS if possible.'))

    def AddAT(self, names, connections, helps):
        names.append('at')
        connections.append(_('AT based'))
        if self.manufacturer in ['symbian', 'nokia']:
            helps.append(_('This provides minimal access to phone features. It is recommended to use other connection type.'))
        else:
            helps.append(_('Good choice for most phones except Nokia and Symbian based. Provides access to most phone features.'))

    def GetDrivers(self):
        names = []
        connections = []
        helps = []

        if self.manufacturer == 'nokia':
            self.AddNokia(names, connections, helps)
            self.AddAT(names, connections, helps)
            self.AddOBEX(names, connections, helps)
        elif self.manufacturer == 'symbian':
            self.AddSymbian(names, connections, helps)
            self.AddAT(names, connections, helps)
            self.AddOBEX(names, connections, helps)
        elif self.manufacturer == 'nota':
            self.AddAT(names, connections, helps)
            self.AddOBEX(names, connections, helps)
        elif self.manufacturer == 'any':
            self.AddAT(names, connections, helps)
            self.AddOBEX(names, connections, helps)
            self.AddNokia(names, connections, helps)
            self.AddSymbian(names, connections, helps)

        return (names, connections, helps)

    def GetPortType(self):
        if self.gammudriver in [
                'mbus',
                'fbus',
                'dlr3',
                'at',
                'at19200',
                'at38400',
                'at115200',
                'obex',
                'phonetblue',
                'fbusblue',
                'fbus-nodtr',
                'dku5-nodtr']:
            if self.connection == 'serial':
                return 'serial'
            elif self.connection == 'bluetooth':
                return 'btserial'
            elif self.connection == 'irda':
                return 'irdaserial'
            elif self.connection == 'usb':
                return 'usbserial'
            return 'serial'
        if self.gammudriver in [
                'blueat',
                'bluerfat',
                'blueobex',
                'bluerfobex',
                'bluerfgnapbus',
                'bluerffbus',
                'bluephonet',
                'bluerfphonet']:
            return 'bluetooth'
        if self.gammudriver in [
                'dku2',
                'dku5',
                'dku2at']:
            return 'dku'
        if self.gammudriver in [
                'irdaat',
                'irdaobex',
                'irdagnapbus',
                'fbusirda',
                'irdaphonet']:
            return 'irda'
        if self.gammudriver is None:
            return None
        # fallback
        return None

    def GetBluezDevices(self):
        try:
            import bluetooth
            return bluetooth.discover_devices()
        except ImportError:
            return []
        except bluetooth.BluetoothError:
            return []
        except IOError:
            return []

    def CheckDev(self, dev):
        res = Wammu.Utils.CheckDeviceNode(dev)
        if res[0] == 0:
            return True
        else:
            return False

    def AddDevs(self, lst, format, limit):
        for x in range(limit):
            name = format % x
            if self.CheckDev(name):
                lst.append(name)


    def GetDevicesWindows(self):
        type = self.GetPortType()
        result = []
        if type in ['serial', 'btserial', 'irdaserial', 'usbserial', None]:
            self.AddDevs(result, 'COM%d', COM_PORTS)
        if type in ['bluetooth', None]:
            result += self.GetBluezDevices()

        help = ''
        if type == 'serial':
            help = _('Enter device name of serial port.')
        elif type in ['btserial', 'irdaserial', 'usbserial']:
            help = _('Enter device name of emulated serial port.')
        elif type == 'bluetooth':
            help = _('Enter Bluetooth address of your phone.')
        elif type in ['irda', 'dku']:
            help = _('You don\'t have to enter anything for this settings.')

        return result, help

    def GetDevicesUNIX(self):
        type = self.GetPortType()
        result = []
        if type in ['serial', None]:
            self.AddDevs(result, '/dev/cua%d', UNX_DEVICES)
            self.AddDevs(result, '/dev/ttyS%d', UNX_DEVICES)
            self.AddDevs(result, '/dev/tts/%d', UNX_DEVICES)
        if type in ['btserial', None]:
            self.AddDevs(result, '/dev/rfcomm%d', UNX_DEVICES)
        if type in ['irdaserial', None]:
            self.AddDevs(result, '/dev/ircomm%d', UNX_DEVICES)
        if type in ['usbserial', 'dku', None]:
            self.AddDevs(result, '/dev/ttyACM%d', UNX_DEVICES)
            self.AddDevs(result, '/dev/ttyUSB%d', UNX_DEVICES)
            self.AddDevs(result, '/dev/usb/tts/%d', UNX_DEVICES)
            self.AddDevs(result, '/dev/usb/acm/%d', UNX_DEVICES)
            self.AddDevs(result, '/dev/input/ttyACM%d', UNX_DEVICES)
        if type in ['bluetooth', None]:
            result += self.GetBluezDevices()

        help = ''
        if type == 'serial':
            help = _('Enter device name of serial port.')
        elif type in ['btserial', 'irdaserial']:
            help = _('Enter device name of emulated serial port.')
        elif type == 'bluetooth':
            help = _('Enter Bluetooth address of your phone.')
        elif type in ['usbserial', 'dku']:
            help = _('Enter device name of USB port.')
        elif type in ['irda', 'dku']:
            help = _('You don\'t have to enter anything for this settings.')

        return result, help


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
            if self.connection != 'bluetooth':
                names.append('at')
                connections.append(_('Generic AT over serial line or it\'s emulation'))
                helps.append(_('Select this if you have real serial port or it is emulated by phone driver (eg. virtual COM port, /dev/rfcomm, /dev/ircomm, etc.).'))

            if self.connection == 'serial':
                for rate in [19200, 38400, 115200]:
                    names.append('at%d' % rate)
                    connections.append(_('Generic AT at %d bps') % rate)
                    helps.append(_('Select this if your phone requires transfer speed %d bps.') % rate)

            elif self.connection == 'bluetooth':
                names.append('blueat')
                connections.append(_('AT over Bluetooth'))
                helps.append(_('Select this if your phone is connected over Bluetooth and you want to use native Bluetooth connection.'))

                names.append('at')
                connections.append(_('Generic AT over serial line or it\'s emulation'))
                helps.append(_('Select this if you have real serial port or it is emulated by phone driver (eg. virtual COM port, /dev/rfcomm, /dev/ircomm, etc.).'))

                names.append('bluerfat')
                connections.append(_('AT over Bluetooth with RF searching'))
                helps.append(_('Use for Bluetooth stack and 6210 / DCT4 Nokia models, which don\'t inform about Bluetooth services correctly (6310, 6310i with firmware lower than 5.50, 8910,..)'))

            elif self.connection == 'irda':
                names.append('irdaat')
                connections.append(_('AT over IrDA'))
                helps.append(_('Select this if your phone is connected over IrDA and you want to use native IrDA connection.'))

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
                helps.append(_('Select this if your phone is connected over IrDA and you want to use native IrDA connection.'))

        elif self.driver == 'symbian':
            if self.connection == 'bluetooth':
                names.append('bluerfgnapbus')
                connections.append(_('Gnapplet over Bluetooth'))
                helps.append(_('Select this if your phone is connected over Bluetooth and you want to use native Bluetooth connection.'))

            elif self.connection == 'irda':
                names.append('irdagnapbus')
                connections.append(_('Gnapplet over IrDA'))
                helps.append(_('Select this if your phone is connected over IrDA and you want to use native IrDA connection.'))

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

            # Serial should not be here, but we do not trust people they really have serial :-)
            if self.connection in ['serial', 'usb']:
                names.append('dku5')
                connections.append(_('DKU5 cable'))
                helps.append(_('Nokia Connectivity Adapter Cable DKU-5 (original cable or compatible), for phones with USB chip like Nokia 5100.'))

                names.append('fbuspl2303')
                connections.append(_('PL2303 cable'))
                helps.append(_('New Nokia protocol for PL2303 USB cable (usually third party cables), for phones with USB chip like Nokia 5100.'))

                names.append('dku2')
                connections.append(_('DKU2 cable'))
                helps.append(_('Nokia Connectivity Cable DKU-2 (original cable or compatible), for phones without USB chip like Nokia 6230.'))

                names.append('dlr3')
                connections.append(_('DLR3-3P/CA-42 cable'))
                helps.append(_('Nokia RS-232 Adapter Cable DLR-3P (original cable or compatible), usually with phones like Nokia 7110/6210/6310.'))

                names.append('fbus-nodtr')
                connections.append(_('FBUS proprietary protocol using ARK cable'))
                helps.append(_('ARK cable (third party cable) for phones not supporting AT commands like Nokia 6020.'))

                names.append('dku5-nodtr')
                connections.append(_('DKU5 phone with ARK cable'))
                helps.append(_('ARK cable (third party cable) for phones with USB chip like Nokia 5100.'))

            elif self.connection == 'bluetooth':
                names.append('bluephonet')
                connections.append(_('Phonet over Bluetooth'))
                helps.append(_('Nokia protocol for Bluetooth stack with other DCT4 Nokia models.'))

                names.append('fbusblue')
                connections.append(_('FBUS over Bluetooth (emulated serial port)'))
                helps.append(
                    _('Nokia protocol for Bluetooth stack with Nokia 6210.') +
                    ' ' +
                    _('Using emulated serial port.')
                )

                names.append('phonetblue')
                connections.append(_('Phonet over Bluetooth (emulated serial port)'))
                helps.append(
                    _('Nokia protocol for Bluetooth stack with other DCT4 Nokia models.') +
                    ' ' +
                    _('Using emulated serial port.')
                )

                names.append('bluerffbus')
                connections.append(_('FBUS over Bluetooth'))
                helps.append(_('Nokia protocol for Bluetooth stack with Nokia 6210.'))

                names.append('bluerfphonet')
                connections.append(_('Phonet over Bluetooth with RF searching'))
                helps.append(_('Nokia protocol for Bluetooth stack with DCT4 Nokia models, which don\'t inform about services correctly (6310, 6310i with firmware lower than 5.50, 8910,..).'))

            elif self.connection == 'irda':
                names.append('irdaphonet')
                connections.append(_('Phonet over IrDA'))
                helps.append(_('Nokia protocol for infrared with other Nokia models.'))

                names.append('fbusirda')
                connections.append(_('FBUS over IrDA'))
                helps.append(_('Nokia protocol for infrared with Nokia 6110/6130/6150.'))

        return (names, connections, helps)
