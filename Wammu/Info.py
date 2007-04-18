import Wammu.Thread
import gammu

class GetInfo(Wammu.Thread.Thread):
    def run(self):
        self.ShowProgress(0)

        data = []

        if self.canceled:
            self.Canceled()
            return

        try:
            Manufacturer = self.sm.GetManufacturer()
            data.append(['Manufacturer', Manufacturer])
        except gammu.GSMError, val:
            self.ShowError(val[0])
          
        if self.canceled:
            self.Canceled()
            return

        self.ShowProgress(12)
        try:
            Model = self.sm.GetModel()
            data.append(['Model (Gammu identification)', Model[0]])
            data.append(['Model (real)', Model[1]])
        except gammu.GSMError, val:
            self.ShowError(val[0])
            
        if self.canceled:
            self.Canceled()
            return

        self.ShowProgress(25)
        try:
            Firmware = self.sm.GetFirmware()
            data.append(['Firmware', Firmware])
        except gammu.GSMError, val:
            self.ShowError(val[0])
            
        if self.canceled:
            self.Canceled()
            return

        self.ShowProgress(37)
        try:
            IMEI = self.sm.GetIMEI()
            data.append(['IMEI', IMEI])
        except gammu.GSMError, val:
            self.ShowError(val[0])
            
        if self.canceled:
            self.Canceled()
            return

        self.ShowProgress(50)
        try:
            OriginalIMEI = self.sm.GetOriginalIMEI()
            data.append(['OriginalIMEI', OriginalIMEI])
        except gammu.GSMError, val:
            self.ShowError(val[0])
            
        if self.canceled:
            self.Canceled()
            return

        self.ShowProgress(42)
        try:
            ProductCode = self.sm.GetProductCode()
            data.append(['ProductCode', ProductCode])
        except gammu.GSMError, val:
            self.ShowError(val[0])
            
        if self.canceled:
            self.Canceled()
            return

        self.ShowProgress(75)
        try:
            SIMIMSI = self.sm.GetSIMIMSI()
            data.append(['SIM IMSI', SIMIMSI])
        except gammu.GSMError, val:
            self.ShowError(val[0])
            
        if self.canceled:
            self.Canceled()
            return

        self.ShowProgress(87)
        try:
            DateTime = self.sm.GetDateTime()
            data.append(['DateTime ', DateTime.strftime('%c')])
        except gammu.GSMError, val:
            self.ShowError(val[0])
           
        if self.canceled:
            self.Canceled()
            return

        self.ShowProgress(100)
        self.SendData(['info','phone'], data)
