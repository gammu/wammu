import Wammu.Thread
import Wammu.Utils
import gammu

class GetCalendar(Wammu.Thread.Thread):
    def run(self):
        self.ShowProgress(0)
        
        try:
            status = self.sm.GetCalendarStatus()
        except gammu.GSMError, val:
            self.ShowError(val[0], True)
            return
 
        remain = status['Used'] 

        data = []
        start = True
        
        while remain > 0:
            self.ShowProgress(100 * (status['Used'] - remain) / status['Used'])
            if self.canceled:
                self.Canceled()
                return
            try:
                if start:
                    value = self.sm.GetNextCalendar(Start = True)
                    start = False
                else:
                    value = self.sm.GetNextCalendar(Location = value['Location'])
            except gammu.GSMError, val:
                self.ShowError(val[0], True)
                return
            Wammu.Utils.ParseCalendar(value)
            data.append(value)
            remain = remain - 1

        self.ShowProgress(100)
        self.SendData(['calendar', '  '], data)
