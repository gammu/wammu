import Wammu.Thread
import gammu

class GetMessage(Wammu.Thread.Thread):
    def run(self):
        self.ShowProgress(0)
        
        try:
            status = self.sm.GetSMSStatus()
        except gammu.GSMError, val:
            self.ShowError(val[0])
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
                self.ShowError(val[0])
                return
            data.append(value)
            remain = remain - 1

        read = []
        unread = []
        sent = []
        unsent = []
        
        for i in data:
            # FIXME: for now we use only first message...
            if i[0]['State'] == 'Read':
                read.append(i[0])
            elif i[0]['State'] == 'UnRead':
                unread.append(i[0])
            elif i[0]['State'] == 'Sent':
                sent.append(i[0])
            elif i[0]['State'] == 'UnSent':
                unsent.append(i[0])
                
        self.SendData(['message', ' R'], read)
        self.SendData(['message', 'UR'], unread)
        self.SendData(['message', ' S'], sent)
        self.SendData(['message', 'US'], unsent)

        self.ShowProgress(100)

