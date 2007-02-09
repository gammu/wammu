# -*- coding: UTF-8 -*-
# vim: expandtab sw=4 ts=4 sts=4:
'''
Wammu - Phone manager
Logging window and thread for log reading
'''
__author__ = 'Michal Čihař'
__email__ = 'michal@cihar.com'
__license__ = '''
Copyright (c) 2003 - 2007 Michal Čihař

This program is free software; you can redistribute it and/or modify it
under the terms of the GNU General Public License version 2 as published by
the Free Software Foundation.

This program is distributed in the hope that it will be useful, but WITHOUT
ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for
more details.

You should have received a copy of the GNU General Public License along with
this program; if not, write to the Free Software Foundation, Inc.,
51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
'''

import threading
import wx
import os
import time
import Wammu.Events

class Logger(threading.Thread):
    def __init__(self, win, file):
        threading.Thread.__init__(self)
        self.win = win
        self.fd = open(file, 'r')
        self.filename = file
        self.canceled = False

    def run(self):
        """
        This is basically tail -f reimplementation
        """
        while not self.canceled:
            where = self.fd.tell()
            txt = self.fd.readline()
            if not txt:
                fd_results = os.fstat(self.fd.fileno())
                try:
                    st_results = os.stat(self.filename)
                except OSError:
                    st_results = fd_results

                if st_results[1] == fd_results[1]:
                    time.sleep(1)
                    self.fd.seek(where)
                else:
                    self.fd = open(self.filename, 'r')
            else:
                evt = Wammu.Events.LogEvent(txt = txt)
                wx.PostEvent(self.win, evt)

class LogFrame(wx.Frame):
    def __init__(self, parent, cfg):
        self.cfg = cfg
        if cfg.HasEntry('/Debug/X') and cfg.HasEntry('/Debug/Y'):
            pos = wx.Point(cfg.ReadInt('/Debug/X'), cfg.ReadInt('/Debug/Y'))
        else:
            pos = wx.DefaultPosition
        size = wx.Size(cfg.ReadInt('/Debug/Width'), cfg.ReadInt('/Debug/Height'))
        wx.Frame.__init__(self, parent, -1, 'Wammu debug log', pos, size, wx.DEFAULT_FRAME_STYLE | wx.RESIZE_BORDER)
        self.txt = wx.TextCtrl(self,-1, 'Here will appear debug messages from Gammu...\n',style = wx.TE_MULTILINE | wx.TE_READONLY)
        self.txt.SetFont(wx.Font(9, wx.MODERN, wx.NORMAL, wx.NORMAL))
        Wammu.Events.EVT_LOG(self, self.OnLog)
        wx.EVT_SIZE(self, self.OnSize)
        self.OnSize(None)

    def OnLog(self, evt):
        self.txt.AppendText(evt.txt)

    def OnSize(self, evt):
        w,h = self.GetClientSizeTuple()
        self.txt.SetDimensions(0, 0, w, h)
