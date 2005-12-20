# -*- coding: UTF-8 -*-
# Wammu - Phone manager
# Copyright (c) 2003 - 2005 Michal Čihař
#
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 2 of the License.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for
# more details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
'''
Message reader
'''

import Wammu.Reader
import Wammu.Utils
import Wammu
if Wammu.gammu_error == None:
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
        res = Wammu.Utils.ProcessMessages(data, True)
        self.SendData(['message', 'Read'], res['read'], False)
        self.SendData(['message', 'UnRead'], res['unread'], False)
        self.SendData(['message', 'Sent'], res['sent'], False)
        self.SendData(['message', 'UnSent'], res['unsent'])
