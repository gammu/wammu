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
Logging window and thread for log reading
'''

import threading
import wx
import os
import sys
import time
import Wammu.Events
from Wammu.Locales import ugettext as _


class LoggerDebug(threading.Thread):
    '''
    Thread which reads defined files and prints it to stderr.
    '''
    def __init__(self, filename):
        '''
        Initializes reader on filename, text will be printed to stderr.
        '''
        threading.Thread.__init__(self)
        self.file_descriptor = open(filename, 'r')
        self.filename = filename
        self.canceled = False

    def run(self):
        """
        This is basically tail -f reimplementation
        """
        while not self.canceled:
            where = self.file_descriptor.tell()
            txt = self.file_descriptor.readlines()
            if len(txt) == 0:
                fd_results = os.fstat(self.file_descriptor.fileno())
                try:
                    st_results = os.stat(self.filename)
                except OSError:
                    st_results = fd_results

                if st_results[1] == fd_results[1] or sys.platform == 'win32':
                    time.sleep(1)
                    self.file_descriptor.seek(where)
                else:
                    self.file_descriptor = open(self.filename, 'r')
            else:
                sys.stderr.write(''.join(txt))
        self.file_descriptor.close()

class Logger(threading.Thread):
    '''
    Thread which reads defined files and posts events on change.
    '''
    def __init__(self, win, filename):
        '''
        Initializes reader on filename, events will be sent to win.
        '''
        threading.Thread.__init__(self)
        self.win = win
        self.file_descriptor = open(filename, 'r')
        self.filename = filename
        self.canceled = False

    def run(self):
        """
        This is basically tail -f reimplementation
        """
        while not self.canceled:
            where = self.file_descriptor.tell()
            txt = self.file_descriptor.readlines()
            if len(txt) == 0:
                fd_results = os.fstat(self.file_descriptor.fileno())
                try:
                    st_results = os.stat(self.filename)
                except OSError:
                    st_results = fd_results

                if st_results[1] == fd_results[1] or sys.platform == 'win32':
                    time.sleep(1)
                    self.file_descriptor.seek(where)
                else:
                    self.file_descriptor = open(self.filename, 'r')
            else:
                evt = Wammu.Events.LogEvent(txt=''.join(txt))
                wx.PostEvent(self.win, evt)
        self.file_descriptor.close()

class LogFrame(wx.Frame):
    '''
    Window with debug log.
    '''

    def __init__(self, parent, cfg):
        '''
        Creates window and initializes event handlers.
        '''
        self.cfg = cfg
        if cfg.HasEntry('/Debug/X') and cfg.HasEntry('/Debug/Y'):
            pos = wx.Point(
                    cfg.ReadInt('/Debug/X'),
                    cfg.ReadInt('/Debug/Y'))
        else:
            pos = wx.DefaultPosition
        size = wx.Size(
            cfg.ReadInt('/Debug/Width'),
            cfg.ReadInt('/Debug/Height')
        )
        wx.Frame.__init__(
            self,
            parent,
            -1,
            _('Wammu debug log'),
            pos,
            size,
            wx.DEFAULT_FRAME_STYLE | wx.RESIZE_BORDER
        )
        self.txt = wx.TextCtrl(
            self,
            -1,
            _('Here will appear debug messages from Gammu...\n'),
            style=wx.TE_MULTILINE | wx.TE_READONLY
        )
        self.txt.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.NORMAL))
        Wammu.Events.EVT_LOG(self, self.OnLog)
        wx.EVT_SIZE(self, self.OnSize)
        self.OnSize(None)

    def OnLog(self, evt):
        '''
        Event handler for text events from Logger.
        '''
        self.txt.AppendText(evt.txt)

    def OnSize(self, evt):
        '''
        Resize handler to correctly resize text area.
        '''
        width, height = self.GetClientSizeTuple()
        self.txt.SetDimensions(0, 0, width, height)
