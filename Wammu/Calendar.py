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
#
'''
Wammu - Phone manager
Calendar reader
'''

import Wammu.Reader
import Wammu.Utils
import Wammu


class GetCalendar(Wammu.Reader.Reader):
    def GetStatus(self):
        status = self.sm.GetCalendarStatus()
        return status['Used']

    def GetNextStart(self):
        return self.sm.GetNextCalendar(Start=True)

    def GetNext(self, location):
        return self.sm.GetNextCalendar(Location=location)

    def Get(self, location):
        return self.sm.GetCalendar(Location=location)

    def Parse(self, value):
        Wammu.Utils.ParseCalendar(value)

    def Send(self, data):
        self.SendData(['calendar', '  '], data)
