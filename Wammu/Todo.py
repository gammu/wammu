# Wammu - Phone manager
# Copyright (c) 2003-4 Michal Cihar 
#
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 2 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MER- CHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for
# more details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc., 59 Temple
# Place, Suite 330, Boston, MA 02111-1307 USA
'''
Todo reader
'''

import Wammu.Reader
import Wammu.Utils
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
