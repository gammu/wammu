# -*- coding: UTF-8 -*-
#
# Copyright © 2003 - 2015 Michal Čihař <michal@cihar.com>
#
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License version 2 as published by
# the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for
# more details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
#
# vim: expandtab sw=4 ts=4 sts=4:
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
