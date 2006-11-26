# -*- coding: UTF-8 -*-
# vim: expandtab sw=4 ts=4 sts=4:
'''
Wammu - Phone manager
Phone number validator
'''
__author__ = 'Michal Čihař'
__email__ = 'michal@cihar.com'
__license__ = '''
Copyright (c) 2003 - 2006 Michal Čihař

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

import wx
import re
from Wammu.Utils import Str_ as _

validchars = '0123456789+#*'
matcher = re.compile('^\\+?[0-9*#]+$')
matcherp = re.compile('^\\+?[P0-9*#]+$')
matchsplit = re.compile('[\s;,]+')

def SplitNumbers(text):
    list = matchsplit.split(text)
    if list[0] == '':
        del list[0]
    if len(list) > 0 and list[len(list) - 1] == '':
        del list[len(list) - 1]
    return list

class PhoneValidator(wx.PyValidator):
    def __init__(self, multi=False, pause=False, empty=False):
        wx.PyValidator.__init__(self)
        self.multi = multi
        self.pause = pause
        self.empty = empty
        wx.EVT_CHAR(self, self.OnChar)

    def Clone(self):
        return PhoneValidator(self.multi, self.pause, self.empty)

    def TransferToWindow(self):
        return True

    def TransferFromWindow(self):
        return True

    def CheckText(self, text, immediate = False):
        if self.multi:
            values = SplitNumbers(text)
        else:
            values = [text]
        for val in values:
            if val == '':
                result = self.empty
            elif not immediate or val != '+':
                if self.pause:
                    if matcherp.match(val) == None:
                        return False
                else:
                    if matcher.match(val) == None:
                        return False
        return True

    def Validate(self, win = None):
        tc = self.GetWindow()
        val = tc.GetValue()

        result = self.CheckText(val)

        if not result and win != None:
            wx.MessageDialog(win,
                _('You did not specify valid phone number.'),
                _('Invalid phone number'),
                wx.OK | wx.ICON_WARNING).ShowModal()
            tc.SetFocus()

        return result

    def OnChar(self, event):
        key = event.KeyCode()

        # control chars
        if key < wx.WXK_SPACE or key == wx.WXK_DELETE or key > 255 or event.AltDown() or event.CmdDown() or event.ControlDown() or event.MetaDown():
            event.Skip()
            return

        try:
            char = chr(key)
            tc = self.GetWindow()
            pos = tc.GetInsertionPoint()
            val = tc.GetValue()
            newval = val[0:pos] + char + val[pos:len(val)]
            if self.CheckText(newval, immediate = True):
                event.Skip()
                return
        except UnicodeDecodeError:
            pass

        # should we bell?
        if not wx.Validator_IsSilent():
            wx.Bell()

        # Returning without calling even.Skip eats the event before it
        # gets to the text control
        return

