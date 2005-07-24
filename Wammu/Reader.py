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
Generic reader class
'''

import Wammu.Thread
import gammu

class Reader(Wammu.Thread.Thread):
    def FallBackStatus(self):
        return 200

    def Run(self):
        self.ShowProgress(0)

        guess = False
        try:
            total = self.GetStatus()
        except gammu.GSMError, val:
            guess = True
            total = self.FallBackStatus()

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
                value['Synced'] = True
                data.append(value)
                remain = remain - 1
        except (gammu.ERR_NOTSUPPORTED, gammu.ERR_NOTIMPLEMENTED):
            location = 1
            empty = 0
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
                    # If we didn't know count and reached end, try some more entries
                    if remain == 0 and guess:
                        remain = 20
                        total = total + 20
                    empty = 0
                except gammu.ERR_EMPTY:
                    empty = empty + 1
                    # If we didn't know count and saw many empty entries, stop right now
                    if empty >= 20 and guess:
                        break
                    pass
                except gammu.GSMError, val:
                    self.ShowError(val[0], True)
                    return
                location = location + 1
        except gammu.GSMError, val:
            self.ShowError(val[0], True)
            return

        self.Send(data)
