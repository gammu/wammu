import Wammu.Reader
import Wammu.Utils
import gammu

class GetMemory(Wammu.Reader.Reader):
    def __init__(self, win, sm, datatype, type):
        Wammu.Reader.Reader.__init__(self, win, sm)
        self.datatype = datatype
        self.type = type

    def GetStatus(self):
        status = self.sm.GetMemoryStatus(Type = self.type)
        return status['Used'] 
        
    def GetNextStart(self):
        return self.sm.GetNextMemory(Start = True, Type = self.type)

    def GetNext(self, location):
        return self.sm.GetNextMemory(Location = location, Type = self.type)
                        
    def Get(self, location):
        return self.sm.GetMemory(Location = location, Type = self.type)

    def Parse(self, value):
        Wammu.Utils.ParseMemoryEntry(value)

    def Send(self, data):
        self.SendData([self.datatype, self.type], data)
