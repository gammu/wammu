# -*- coding: UTF-8 -*-
# Wammu - Phone manager
# Copyright (c) 2003 - 2004 Michal Čihař 
#
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 2 of the License.
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
Phone information reader
'''

import Wammu.Thread
import gammu
from Wammu.Utils import Str_ as _

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
            data.append([_('Manufacturer'), Manufacturer])
        except (gammu.ERR_NOTSUPPORTED, gammu.ERR_NOTIMPLEMENTED):
            pass 
        except gammu.GSMError, val:
            self.ShowError(val[0])
          
        if self.canceled:
            self.Canceled()
            return

        self.ShowProgress(1*100/progress)
        try:
            Model = self.sm.GetModel()
            data.append([_('Model (Gammu identification)'), Model[0]])
            data.append([_('Model (real)'), Model[1]])
        except (gammu.ERR_NOTSUPPORTED, gammu.ERR_NOTIMPLEMENTED):
            pass 
        except gammu.GSMError, val:
            self.ShowError(val[0])
            
        if self.canceled:
            self.Canceled()
            return

        self.ShowProgress(2*100/progress)
        try:
            Firmware = self.sm.GetFirmware()
            data.append([_('Firmware'), Firmware[0]])
            if Firmware[1] != '':
                data.append([_('Firmware date'), Firmware[1]])
            if Firmware[2] != 0.0:
                data.append([_('Firmware (numeric)'), str(Firmware[2])])
        except (gammu.ERR_NOTSUPPORTED, gammu.ERR_NOTIMPLEMENTED):
            pass 
        except gammu.GSMError, val:
            self.ShowError(val[0])
            
        if self.canceled:
            self.Canceled()
            return

        self.ShowProgress(3*100/progress)
        try:
            IMEI = self.sm.GetIMEI()
            data.append([_('Serial number (IMEI)'), IMEI])
        except (gammu.ERR_NOTSUPPORTED, gammu.ERR_NOTIMPLEMENTED):
            pass 
        except gammu.GSMError, val:
            self.ShowError(val[0])
            
        if self.canceled:
            self.Canceled()
            return

        self.ShowProgress(4*100/progress)
        try:
            OriginalIMEI = self.sm.GetOriginalIMEI()
            data.append([_('Original IMEI'), OriginalIMEI])
        except (gammu.ERR_NOTSUPPORTED, gammu.ERR_NOTIMPLEMENTED):
            pass 
        except gammu.GSMError, val:
            self.ShowError(val[0])
            
        if self.canceled:
            self.Canceled()
            return

        self.ShowProgress(5*100/progress)
        try:
            ProductCode = self.sm.GetProductCode()
            data.append([_('Product code'), ProductCode])
        except (gammu.ERR_NOTSUPPORTED, gammu.ERR_NOTIMPLEMENTED):
            pass 
        except gammu.GSMError, val:
            self.ShowError(val[0])
            
        if self.canceled:
            self.Canceled()
            return

        self.ShowProgress(6*100/progress)
        try:
            SIMIMSI = self.sm.GetSIMIMSI()
            data.append([_('SIM IMSI'), SIMIMSI])
        except (gammu.ERR_NOTSUPPORTED, gammu.ERR_NOTIMPLEMENTED):
            pass 
        except gammu.GSMError, val:
            self.ShowError(val[0])
            
        if self.canceled:
            self.Canceled()
            return

        self.ShowProgress(7*100/progress)
        try:
            SMSC = self.sm.GetSMSC()
            data.append([_('SMSC'), SMSC['Number']])
        except (gammu.ERR_NOTSUPPORTED, gammu.ERR_NOTIMPLEMENTED):
            pass 
        except gammu.GSMError, val:
            self.ShowError(val[0])
           
        if self.canceled:
            self.Canceled()
            return

        self.ShowProgress(8*100/progress)
        try:
            info = self.sm.GetHardware()
            data.append([_('Hardware'), info])
        except (gammu.ERR_NOTSUPPORTED, gammu.ERR_NOTIMPLEMENTED):
            pass 
        except gammu.GSMError, val:
            self.ShowError(val[0])
           
        if self.canceled:
            self.Canceled()
            return

        self.ShowProgress(9*100/progress)
        try:
            info = self.sm.GetManufactureMonth()
            data.append([_('Manufacture month'), info])
        except (gammu.ERR_NOTSUPPORTED, gammu.ERR_NOTIMPLEMENTED):
            pass 
        except gammu.GSMError, val:
            self.ShowError(val[0])
           
        if self.canceled:
            self.Canceled()
            return

        self.ShowProgress(10*100/progress)
        try:
            info = self.sm.GetPPM()
            data.append([_('Language packs in phone'), info])
        except (gammu.ERR_NOTSUPPORTED, gammu.ERR_NOTIMPLEMENTED):
            pass 
        except gammu.GSMError, val:
            self.ShowError(val[0])
           
        if self.canceled:
            self.Canceled()
            return

        self.ShowProgress(100)
        self.SendData(['info','phone'], data)
