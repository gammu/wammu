import Wammu.Reader
import Wammu.Utils
import gammu

class GetMessage(Wammu.Reader.Reader):
    def GetStatus(self):
        status = self.sm.GetSMSStatus()
        return status['SIMUsed'] + status['PhoneUsed'] + status['TemplatesUsed']
        
    def GetNextStart(self):
        return self.sm.GetNextSMS(Start = True, Folder = 0)

    def GetNext(self, location):
        return self.sm.GetNextSMS(Location = location, Folder = 0)
                        
    def Get(self, location):
        return self.sm.GetSMS(Location = location, Folder = 0)

    def Parse(self, value):
        return

    def Send(self, data):
        read = []
        unread = []
        sent = []
        unsent = []
        data = gammu.LinkSMS(data)
        
        for x in data:
            i = {}
            v = gammu.DecodeSMS(x)
            i['SMS'] = x
            if v != None:
                i['SMSInfo'] = v
            Wammu.Utils.ParseMessage(i, (v != None))
            if i['State'] == 'Read':
                read.append(i)
            elif i['State'] == 'UnRead':
                unread.append(i)
            elif i['State'] == 'Sent':
                sent.append(i)
            elif i['State'] == 'UnSent':
                unsent.append(i)
                
        self.SendData(['message', 'Read'], read, False)
        self.SendData(['message', 'UnRead'], unread, False)
        self.SendData(['message', 'Sent'], sent, False)
        self.SendData(['message', 'UnSent'], unsent)
