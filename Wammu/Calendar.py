import Wammu.Reader
import Wammu.Utils
import gammu

class GetCalendar(Wammu.Reader.Reader):
    def GetStatus(self):
        status = self.sm.GetCalendarStatus()
        return status['Used'] 
        
    def GetNextStart(self):
        return self.sm.GetNextCalendar(Start = True)

    def GetNext(self, location):
        return self.sm.GetNextCalendar(Location = location)
                        
    def Get(self, location):
        return self.sm.GetCalendar(Location = location)

    def Parse(self, value):
        Wammu.Utils.ParseCalendar(value)

    def Send(self, data):
        self.SendData(['calendar', '  '], data)
