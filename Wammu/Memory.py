# -*- coding: UTF-8 -*-
#
# Copyright © 2003 - 2018 Michal Čihař <michal@cihar.com>
#
# This file is part of Wammu <https://wammu.eu/>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
'''
Wammu - Phone manager
Memory reader
'''

import Wammu.Reader
import Wammu.Utils
import Wammu

class GetMemory(Wammu.Reader.Reader):
    def __init__(self, win, sm, datatype, type):
        Wammu.Reader.Reader.__init__(self, win, sm)
        self.datatype = datatype
        self.type = type

    def FallBackStatus(self):
        if self.type in ['MC', 'DC', 'RC']:
            # guess smaller values for calls, as this memory is usually much smaller
            return 40
        else:
            return Wammu.Reader.Reader.FallBackStatus(self)

    def GetStatus(self):
        status = self.sm.GetMemoryStatus(Type=self.type)
        return status['Used']

    def GetNextStart(self):
        return self.sm.GetNextMemory(Start=True, Type=self.type)

    def GetNext(self, location):
        return self.sm.GetNextMemory(Location=location, Type=self.type)

    def Get(self, location):
        return self.sm.GetMemory(Location=location, Type=self.type)

    def Parse(self, value):
        Wammu.Utils.ParseMemoryEntry(value, self.win.cfg)

    def Send(self, data):
        self.SendData([self.datatype, self.type], data)
