import Wammu.Thread
import Wammu.Utils
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
                        value = self.sm.GetNextMemory(Start = True, Type = self.type)
                        start = False
                    else:
                        value = self.sm.GetNextMemory(Location = value['Location'], Type = self.type)
                except gammu.ERR_EMPTY:
                    break

                Wammu.Utils.ParseMemoryEntry(value)
                data.append(value)
                remain = remain - 1
        except (gammu.ERR_NOTSUPPORTED, gammu.ERR_NOTIMPLEMENTED):
            location = 1
            while remain > 0:
                self.ShowProgress(100 * (total - remain) / total)
                if self.canceled:
                    self.Canceled()
                    return
                try:
                    value = self.sm.GetMemory(Type = self.type, Location = location)
                    Wammu.Utils.ParseMemoryEntry(value)
                    data.append(value)
                    remain = remain - 1
                except gammu.ERR_EMPTY:
                    pass
                except gammu.GSMError, val:
                    self.ShowError(val[0], True)
                    return
                location = location + 1
        except gammu.GSMError, val:
            self.ShowError(val[0], True)
            return

        self.ShowProgress(100)
        self.SendData([self.datatype, self.type], data)
