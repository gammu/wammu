# -*- coding: UTF-8 -*-
#
# Copyright © 2003 - 2017 Michal Čihař <michal@cihar.com>
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
webbrowser wrapper
'''

import webbrowser
import threading


class BrowserThread(threading.Thread):
    '''
    Thread which opens URL in browser.
    '''

    def __init__(self, url):
        '''
        Creates new BrowserThread object.

        @param url: URL to open when thread is started.
        '''
        threading.Thread.__init__(self)
        self._url = url

    def run(self):
        '''
        Actually opens browser.
        '''
        webbrowser.open(self._url)


def Open(url):
    '''
    Convenience wrapper to open URL in browser without blocking main
    thread.
    '''
    BrowserThread(url).start()
