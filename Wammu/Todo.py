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
        
        while remain > 0:
            self.ShowProgress(100 * (status['Used'] - remain) / status['Used'])
            if self.canceled:
                self.Canceled()
                return
            try:
                if start:
                    value = self.sm.GetNextToDo(Start = True)
                    start = False
                else:
                    value = self.sm.GetNextToDo(Location = value['Location'])
            except gammu.GSMError, val:
                self.ShowError(val[0], True)
                return
            Wammu.Utils.ParseTodo(value)
            data.append(value)
            remain = remain - 1

        self.ShowProgress(100)
        self.SendData(['todo', '  '], data)
