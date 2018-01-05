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
Bluetooth discovery helper
'''

import bluetooth


class Discovery(bluetooth.DeviceDiscoverer):
    '''
    Discovery helper class. It just passes all found devices to parent
    AllSearchThread.
    '''
    def __init__(self, parent):
        bluetooth.DeviceDiscoverer.__init__(self)
        self.parent = parent

    def device_discovered(self, address, device_class, name):
        '''
        Called when device is iscovered, checks device class and if it is
        phone, it calls search_bt_device method of parent.
        '''
        major_class = (device_class & 0xf00) >> 8
        # We want only devices with phone class
        # See https://www.bluetooth.org/apps/content/?doc_id=49706
        if major_class == 2:
            self.parent.search_bt_device(address, name)

    def inquiry_complete(self):
        '''
        Called when discovery is completed, does nothing.
        '''
        return
