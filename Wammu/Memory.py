import Wammu.Thread
import gammu

class GetMemory(Wammu.Thread.Thread):
    def __init__(self, win, sm, datatype, type):
        Wammu.Thread.Thread.__init__(self, win, sm)
        self.datatype = datatype
        self.type = type

    def run(self):
        self.ShowProgress(0)
        
        try:
            status = self.sm.GetMemoryStatus(Type = self.type)
        except gammu.GSMError, val:
            self.ShowError(val[0])
            return
 
        remain = status["Used"] 

        data = []
        
        if remain > 0:
            try:
                value = self.sm.GetNextMemory(Start = True, Type = self.type)
            except gammu.GSMError, val:
                self.ShowError(val[0])
                return
            data.append(value)
            remain = remain - 1
            
        while remain > 0:
            print remain
            print 100 * (status["Used"] - remain) / status["Used"]
            self.ShowProgress(100 * (status["Used"] - remain) / status["Used"])
            if self.canceled:
                self.Canceled()
                return
            try:
                value = self.sm.GetNextMemory(Location = value["Location"], Type = self.type)
            except gammu.GSMError, val:
                self.ShowError(val[0])
                return
            data.append(value)
            remain = remain - 1

        self.ShowProgress(100)
        self.SendData([self.datatype, self.type], data)
