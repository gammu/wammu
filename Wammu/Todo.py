# -*- coding: UTF-8 -*-
# Wammu - Phone manager
# Copyright (c) 2003 - 2006 Michal Čihař
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
Todo reader
'''

import Wammu.Reader
import Wammu.Utils
import Wammu
if Wammu.gammu_error == None:
    import gammu

class GetTodo(Wammu.Reader.Reader):
    def GetStatus(self):
        status = self.sm.GetToDoStatus()
        return status['Used']

    def GetNextStart(self):
        return self.sm.GetNextToDo(Start = True)

    def GetNext(self, location):
        return self.sm.GetNextToDo(Location = location)

    def Get(self, location):
        return self.sm.GetToDo(Location = location)

    def Parse(self, value):
        Wammu.Utils.ParseTodo(value)

    def Send(self, data):
        self.SendData(['todo', '  '], data)
