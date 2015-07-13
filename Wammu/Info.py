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
Phone information reader
'''

import Wammu.Thread
from Wammu.Locales import ugettext as _
if Wammu.gammu_error is None:
    import gammu

class GetInfo(Wammu.Thread.Thread):
    def Run(self):
        self.ShowProgress(0)

        progress = 12

        data = []

        if self.canceled:
            self.Canceled()
            return

        try:
            Manufacturer = self.sm.GetManufacturer()
            data.append({'Name': _('Manufacturer'), 'Value': Manufacturer, 'Synced': True})
        except (gammu.ERR_NOTSUPPORTED, gammu.ERR_NOTIMPLEMENTED):
            pass
        except gammu.GSMError, val:
            self.ShowError(val.args[0])

        if self.canceled:
            self.Canceled()
            return

        self.ShowProgress(1*100/progress)
        try:
            Model = self.sm.GetModel()
            data.append({'Name': _('Model (Gammu identification)'), 'Value': Model[0], 'Synced': True})
            data.append({'Name': _('Model (real)'), 'Value': Model[1], 'Synced': True})
        except (gammu.ERR_NOTSUPPORTED, gammu.ERR_NOTIMPLEMENTED):
            pass
        except gammu.GSMError, val:
            self.ShowError(val.args[0])

        if self.canceled:
            self.Canceled()
            return

        self.ShowProgress(2*100/progress)
        try:
            Firmware = self.sm.GetFirmware()
            data.append({'Name': _('Firmware'), 'Value': Firmware[0], 'Synced': True})
            if Firmware[1] != '':
                data.append({'Name': _('Firmware date'), 'Value': Firmware[1], 'Synced': True})
            if Firmware[2] != 0.0:
                data.append({'Name': _('Firmware (numeric)'), 'Value': str(Firmware[2]), 'Synced': True})
        except (gammu.ERR_NOTSUPPORTED, gammu.ERR_NOTIMPLEMENTED):
            pass
        except gammu.GSMError, val:
            self.ShowError(val.args[0])

        if self.canceled:
            self.Canceled()
            return

        self.ShowProgress(3*100/progress)
        try:
            IMEI = self.sm.GetIMEI()
            data.append({'Name': _('Serial number (IMEI)'), 'Value': IMEI, 'Synced': True})
        except (gammu.ERR_NOTSUPPORTED, gammu.ERR_NOTIMPLEMENTED):
            pass
        except gammu.GSMError, val:
            self.ShowError(val.args[0])

        if self.canceled:
            self.Canceled()
            return

        self.ShowProgress(4*100/progress)
        try:
            OriginalIMEI = self.sm.GetOriginalIMEI()
            data.append({'Name': _('Original IMEI'), 'Value': OriginalIMEI, 'Synced': True})
        except (gammu.ERR_NOTSUPPORTED, gammu.ERR_NOTIMPLEMENTED):
            pass
        except gammu.GSMError, val:
            self.ShowError(val.args[0])

        if self.canceled:
            self.Canceled()
            return

        self.ShowProgress(5*100/progress)
        try:
            ProductCode = self.sm.GetProductCode()
            data.append({'Name': _('Product code'), 'Value': ProductCode, 'Synced': True})
        except (gammu.ERR_NOTSUPPORTED, gammu.ERR_NOTIMPLEMENTED):
            pass
        except gammu.GSMError, val:
            self.ShowError(val.args[0])

        if self.canceled:
            self.Canceled()
            return

        self.ShowProgress(6*100/progress)
        try:
            try:
                SIMIMSI = self.sm.GetSIMIMSI()
            except (gammu.ERR_SECURITYERROR):
                SIMIMSI = _('N/A')
            data.append({'Name': _('SIM IMSI'), 'Value': SIMIMSI, 'Synced': True})
        except (gammu.ERR_NOTSUPPORTED, gammu.ERR_NOTIMPLEMENTED):
            pass
        except gammu.GSMError, val:
            self.ShowError(val.args[0])

        if self.canceled:
            self.Canceled()
            return

        self.ShowProgress(7*100/progress)
        try:
            try:
                SMSC = self.sm.GetSMSC()['Number']
            except (gammu.ERR_SECURITYERROR):
                SMSC = _('N/A')
            data.append({'Name': _('SMSC'), 'Value': SMSC, 'Synced': True})
        except (gammu.ERR_NOTSUPPORTED, gammu.ERR_NOTIMPLEMENTED, gammu.ERR_EMPTY):
            pass
        except gammu.GSMError, val:
            self.ShowError(val.args[0])

        if self.canceled:
            self.Canceled()
            return

        self.ShowProgress(8*100/progress)
        try:
            info = self.sm.GetHardware()
            data.append({'Name': _('Hardware'), 'Value': info, 'Synced': True})
        except (gammu.ERR_NOTSUPPORTED, gammu.ERR_NOTIMPLEMENTED):
            pass
        except gammu.GSMError, val:
            self.ShowError(val.args[0])

        if self.canceled:
            self.Canceled()
            return

        self.ShowProgress(9*100/progress)
        try:
            info = self.sm.GetManufactureMonth()
            data.append({'Name': _('Manufacture month'), 'Value': info, 'Synced': True})
        except (gammu.ERR_NOTSUPPORTED, gammu.ERR_NOTIMPLEMENTED):
            pass
        except gammu.GSMError, val:
            self.ShowError(val.args[0])

        if self.canceled:
            self.Canceled()
            return

        self.ShowProgress(10*100/progress)
        try:
            info = self.sm.GetPPM()
            data.append({'Name': _('Language packs in phone'), 'Value': info, 'Synced': True})
        except (gammu.ERR_NOTSUPPORTED, gammu.ERR_NOTIMPLEMENTED):
            pass
        except gammu.GSMError, val:
            self.ShowError(val.args[0])

        if self.canceled:
            self.Canceled()
            return

        self.ShowProgress(100)
        self.SendData(['info', 'phone'], data)
