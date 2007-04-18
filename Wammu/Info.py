import Wammu.Thread
import gammu

class GetInfo(Wammu.Thread.Thread):
    def run(self):
        self.ShowProgress(0)

        progress = 9

        data = []

        if self.canceled:
            self.Canceled()
            return

        try:
            Manufacturer = self.sm.GetManufacturer()
            data.append([_('Manufacturer'), Manufacturer])
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
        except gammu.GSMError, val:
            self.ShowError(val[0])
            
        if self.canceled:
            self.Canceled()
            return

        self.ShowProgress(2*100/progress)
        try:
            Firmware = self.sm.GetFirmware()
            data.append([_('Firmware'), Firmware])
        except gammu.GSMError, val:
            self.ShowError(val[0])
            
        if self.canceled:
            self.Canceled()
            return

        self.ShowProgress(3*100/progress)
        try:
            IMEI = self.sm.GetIMEI()
            data.append([_('Serial number (IMEI)'), IMEI])
        except gammu.GSMError, val:
            self.ShowError(val[0])
            
        if self.canceled:
            self.Canceled()
            return

        self.ShowProgress(4*100/progress)
        try:
            OriginalIMEI = self.sm.GetOriginalIMEI()
            data.append([_('Original IMEI'), OriginalIMEI])
        except gammu.GSMError, val:
            self.ShowError(val[0])
            
        if self.canceled:
            self.Canceled()
            return

        self.ShowProgress(5*100/progress)
        try:
            ProductCode = self.sm.GetProductCode()
            data.append([_('Product code'), ProductCode])
        except gammu.GSMError, val:
            self.ShowError(val[0])
            
        if self.canceled:
            self.Canceled()
            return

        self.ShowProgress(6*100/progress)
        try:
            SIMIMSI = self.sm.GetSIMIMSI()
            data.append([_('SIM IMSI'), SIMIMSI])
        except gammu.GSMError, val:
            self.ShowError(val[0])
            
        if self.canceled:
            self.Canceled()
            return

        self.ShowProgress(7*100/progress)
        try:
            SMSC = self.sm.GetSMSC()
            data.append([_('SMSC'), SMSC['Number']])
        except gammu.GSMError, val:
            self.ShowError(val[0])
           
        if self.canceled:
            self.Canceled()
            return

        self.ShowProgress(8*100/progress)
        try:
            DateTime = self.sm.GetDateTime()
            data.append([_('Date and time'), DateTime.strftime('%c')])
        except gammu.GSMError, val:
            self.ShowError(val[0])
           
        if self.canceled:
            self.Canceled()
            return

        self.ShowProgress(100)
        self.SendData(['info','phone'], data)
