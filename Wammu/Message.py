import Wammu.Thread
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
        
        while remain > 0:
            self.ShowProgress(100 * (total - remain) / total)
            if self.canceled:
                self.Canceled()
                return
            try:
                if start:
                    value = self.sm.GetNextSMS(Start = True, Folder = 0)
                    start = False
                else:
                    value = self.sm.GetNextSMS(Location = value[0]['Location'], Folder = 0)
            except gammu.GSMError, val:
                self.ShowError(val[0], True)
                return
            data.append(value)
            remain = remain - 1

        read = []
        unread = []
        sent = []
        unsent = []
        
        for x in data:
            for n in range(len(x)):
                i = x[n]
                if i['State'] == 'Read':
                    i['S'] = ' R'
                    read.append(i)
                elif i['State'] == 'UnRead':
                    i['S'] = 'UR'
                    unread.append(i)
                elif i['State'] == 'Sent':
                    i['S'] = ' S'
                    sent.append(i)
                elif i['State'] == 'UnSent':
                    i['S'] = 'US'
                    unsent.append(i)
                
        self.SendData(['message', ' R'], read, False)
        self.SendData(['message', 'UR'], unread, False)
        self.SendData(['message', ' S'], sent, False)
        self.SendData(['message', 'US'], unsent)

        self.ShowProgress(100)

