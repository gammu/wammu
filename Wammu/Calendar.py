import Wammu.Thread
import Wammu.Utils
import gammu

class GetCalendar(Wammu.Thread.Thread):
    def run(self):
        self.ShowProgress(0)
        
        try:
            status = self.sm.GetCalendarStatus()
            total = remain = status['Used'] 
        except gammu.GSMError, val:
            total = remain = 999

        data = []
        
        try:
            start = True
            while remain > 0:
                self.ShowProgress(100 * (total - remain) / total)
                if self.canceled:
                    self.Canceled()
                    return
                try:
                    if start:
                        value = self.sm.GetNextCalendar(Start = True)
                        start = False
                    else:
                        value = self.sm.GetNextCalendar(Location = value['Location'])
                except gammu.ERR_EMPTY:
                    break
                Wammu.Utils.ParseCalendar(value)
                data.append(value)
                remain = remain - 1
        except gammu.ERR_NOTSUPPORTED:
            location = 1
            while remain > 0:
                self.ShowProgress(100 * (total - remain) / total)
                if self.canceled:
                    self.Canceled()
                    return
                try:
                    value = self.sm.GetCalendar(Location = location)
                    Wammu.Utils.ParseCalendar(value)
                    data.append(value)
                    remain = remain - 1
                except gammu.ERR_EMPTY:
                    pass
                location = location + 1
        except gammu.GSMError, val:
            self.ShowError(val[0], True)
            return

        self.ShowProgress(100)
        self.SendData(['calendar', '  '], data)
