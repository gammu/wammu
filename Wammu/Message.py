import Wammu.Thread
import Wammu.Utils
import gammu

class GetMessage(Wammu.Thread.Thread):
    def run(self):
        self.ShowProgress(0)
        
        try:
            status = self.sm.GetSMSStatus()
        except gammu.GSMError, val:
            self.ShowError(val[0], True)
            return
 
        total = remain = status['SIMUsed'] + status['PhoneUsed']

        data = []
        start = True
        
        try:
            while remain > 0:
                self.ShowProgress(100 * (total - remain) / total)
                if self.canceled:
                    self.Canceled()
                    return
                if start:
                    value = self.sm.GetNextSMS(Start = True, Folder = 0)
                    start = False
                else:
                    value = self.sm.GetNextSMS(Location = value[0]['Location'], Folder = 0)
                data.append(value)
                remain = remain - len(value)
        except gammu.ERR_NOTSUPPORTED:
            location = 1
            while remain > 0:
                self.ShowProgress(100 * (total - remain) / total)
                if self.canceled:
                    self.Canceled()
                    return
                try:
                    value = self.sm.GetSMS(Folder = 0, Location = location)
                    data.append(value)
                    remain = remain - 1
                except gammu.ERR_EMPTY:
                    pass
                location = location + 1
        except gammu.GSMError, val:
            self.ShowError(val[0], True)
            return

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

        self.ShowProgress(100)

