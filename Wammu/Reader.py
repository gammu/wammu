import Wammu.Thread
import gammu

class Reader(Wammu.Thread.Thread):
    def run(self):
        self.ShowProgress(0)
        
        try:
            total = self.GetStatus()
        except gammu.GSMError, val:
            total = 999

        remain = total

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
                        value = self.GetNextStart()
                        start = False
                    else:
                        try:
                            loc = value['Location']
                        except TypeError:
                            loc = value[0]['Location']
                        value = self.GetNext(loc)
                except gammu.ERR_EMPTY:
                    break

                self.Parse(value)
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
                    value = self.Get(location)
                    self.Parse(value)
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

        self.Send(data)

        self.ShowProgress(100)
