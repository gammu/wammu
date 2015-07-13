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
Phone number validator.
'''

import wx
import re
from Wammu.Locales import ugettext as _


MATCHER_NORMAL = re.compile('^[0-9*#+]+$')
MATCHER_PAUSE = re.compile('^[Pp0-9*#+]+$')
MATCH_SPLIT = re.compile('[\s;,]+')

def SplitNumbers(text):
    '''
    Splits text to list of phone numbers.
    '''
    lst = MATCH_SPLIT.split(text)
    if lst[0] == '':
        del lst[0]
    if len(lst) > 0 and lst[len(lst) - 1] == '':
        del lst[len(lst) - 1]
    return lst

class PhoneValidator(wx.PyValidator):
    '''
    Validator for phone numbers.
    '''
    def __init__(self, multi=False, pause=False, empty=False):
        wx.PyValidator.__init__(self)
        self.multi = multi
        self.pause = pause
        self.empty = empty
        self.Bind(wx.EVT_CHAR, self.OnChar)

    def Clone(self):
        return PhoneValidator(self.multi, self.pause, self.empty)

    def TransferToWindow(self):
        return True

    def TransferFromWindow(self):
        return True

    def CheckText(self, text, immediate=False):
        '''
        Verifies whether enterd text is correct.
        '''
        if self.multi:
            values = SplitNumbers(text)
        else:
            values = [text]
        for val in values:
            if val == '' and not self.empty:
                if immediate:
                    continue
                else:
                    return False
            elif self.pause and MATCHER_PAUSE.match(val) is None:
                return False
            elif not self.pause and MATCHER_NORMAL.match(val) is None:
                return False
            elif immediate and val == '+':
                continue
        return True

    def Validate(self, win=None):
        textcontrol = self.GetWindow()
        val = textcontrol.GetValue()

        result = self.CheckText(val)

        if not result and win is not None:
            wx.MessageDialog(
                win,
                _('You did not specify valid phone number.'),
                _('Invalid phone number'),
                wx.OK | wx.ICON_WARNING
            ).ShowModal()
            textcontrol.SetFocus()

        return result

    def OnChar(self, event):
        key = event.GetKeyCode()

        # control chars
        if (key < wx.WXK_SPACE or
                key == wx.WXK_DELETE or
                key > 255 or
                event.AltDown() or
                event.CmdDown() or
                event.ControlDown() or
                event.MetaDown()):
            event.Skip()
            return

        try:
            char = chr(key)
            textcontrol = self.GetWindow()
            pos = textcontrol.GetInsertionPoint()
            val = textcontrol.GetValue()
            newval = val[0:pos] + char + val[pos:len(val)]
            if self.CheckText(newval, immediate=True):
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
