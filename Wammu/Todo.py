import Wammu.Reader
import Wammu.Utils
import gammu

class GetTodo(Wammu.Reader.Reader):
    def GetStatus(self):
        status = self.sm.GetToDoStatus()
        return status['Used'] 
        
    def GetNextStart(self):
        return self.sm.GetNextToDo(Start = True)

    def GetNext(self, location):
        return self.sm.GetNextToDo(Location = location)
                        
    def Get(self, location):
        return self.sm.GetToDo(Location = location)

    def Parse(self, value):
        Wammu.Utils.ParseTodo(value)

    def Send(self, data):
        self.SendData(['todo', '  '], data)
