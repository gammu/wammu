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
# this program; if not, write to the Free Software Foundation, Inc., 59 Temple
# Place, Suite 330, Boston, MA 02111-1307 USA
'''
Message reader
'''

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
