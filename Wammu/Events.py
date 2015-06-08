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
wx events used all around this program.
'''

from wx.lib.newevent import NewEvent

# create some events:
ShowMessageEvent, EVT_SHOW_MESSAGE = NewEvent()
ProgressEvent, EVT_PROGRESS = NewEvent()
LinkEvent, EVT_LINK = NewEvent()
DataEvent, EVT_DATA = NewEvent()
ShowEvent, EVT_SHOW = NewEvent()
EditEvent, EVT_EDIT = NewEvent()
SendEvent, EVT_SEND = NewEvent()
CallEvent, EVT_CALL = NewEvent()
MessageEvent, EVT_MESSAGE = NewEvent()
ReplyEvent, EVT_REPLY = NewEvent()
DuplicateEvent, EVT_DUPLICATE = NewEvent()
DeleteEvent, EVT_DELETE = NewEvent()
LogEvent, EVT_LOG = NewEvent()
TextEvent, EVT_TEXT = NewEvent()
DoneEvent, EVT_DONE = NewEvent()
BackupEvent, EVT_BACKUP = NewEvent()
ExceptionEvent, EVT_EXCEPTION = NewEvent()
