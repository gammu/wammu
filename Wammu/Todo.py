import Wammu.Thread
import Wammu.Utils
import gammu

class GetTodo(Wammu.Thread.Thread):
    def run(self):
        self.ShowProgress(0)
        
        try:
            status = self.sm.GetToDoStatus()
        except gammu.GSMError, val:
            self.ShowError(val[0], True)
            return
 
        remain = status['Used'] 

        data = []
        start = True
        
        try:
            while remain > 0:
                self.ShowProgress(100 * (status['Used'] - remain) / status['Used'])
                if self.canceled:
                    self.Canceled()
                    return
                if start:
                    value = self.sm.GetNextToDo(Start = True)
                    start = False
                else:
                    value = self.sm.GetNextToDo(Location = value['Location'])
                Wammu.Utils.ParseTodo(value)
                data.append(value)
                remain = remain - 1
        except gammu.ERR_NOTSUPPORTED:
            location = 1
            while remain > 0:
                self.ShowProgress(100 * (status['Used'] - remain) / status['Used'])
                if self.canceled:
                    self.Canceled()
                    return
                try:
                    value = self.sm.GetToDo(Location = location)
                    Wammu.Utils.ParseTodo(value)
                    data.append(value)
                    remain = remain - 1
                except gammu.ERR_EMPTY:
                    pass
                location = location + 1
        except gammu.GSMError, val:
            self.ShowError(val[0], True)
            return

        self.ShowProgress(100)
        self.SendData(['todo', '  '], data)
