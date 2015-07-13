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
Generic thread wrapper used for reading things from phone
'''

import sys
import threading
import wx
import Wammu.Events
from Wammu.Locales import ugettext as _


class Thread(threading.Thread):
    def __init__(self, win, sm):
        threading.Thread.__init__(self)
        self.win = win
        self.sm = sm
        self.canceled = False

    def run(self):
        try:
            self.Run()
        except:
            evt = Wammu.Events.ExceptionEvent(data=sys.exc_info())
            wx.PostEvent(self.win, evt)
            self.ShowProgress(100)

    def Cancel(self):
        self.canceled = True

    def ShowError(self, info, finish=False):
        if finish:
            self.ShowProgress(100)
        lck = threading.Lock()
        lck.acquire()
        evt = Wammu.Events.ShowMessageEvent(
            message=Wammu.Utils.FormatError(
                _('Error while communicating with phone'),
                info),
            title=_('Error Occured'),
            type=wx.ICON_ERROR,
            errortype='gammu',
            lock=lck)
        wx.PostEvent(self.win, evt)
        lck.acquire()

    def ShowMessage(self, title, text):
        lck = threading.Lock()
        lck.acquire()
        evt = Wammu.Events.ShowMessageEvent(
            message=text,
            title=title,
            type=wx.ICON_INFORMATION,
            lock=lck)
        wx.PostEvent(self.win, evt)
        lck.acquire()

    def ShowProgress(self, progress):
        evt = Wammu.Events.ProgressEvent(
            progress=progress,
            cancel=self.Cancel)
        wx.PostEvent(self.win, evt)

    def SendData(self, datatype, data, last=True):
        evt = Wammu.Events.DataEvent(
            type=datatype,
            data=data,
            last=last)
        wx.PostEvent(self.win, evt)

    def Canceled(self):
        lck = threading.Lock()
        lck.acquire()
        evt = Wammu.Events.ShowMessageEvent(
            message=_('Action canceled by user!'),
            title=_('Action canceled'),
            type=wx.ICON_WARNING,
            lock=lck)
        wx.PostEvent(self.win, evt)
        lck.acquire()
        self.ShowProgress(100)
