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
Phone number validator
'''

import wx
import re
from Wammu.Utils import Str_ as _

validchars = '0123456789+#*'
matcher = re.compile('^\\+?[0-9*#]+$')
matcherp = re.compile('^\\+?[P0-9*#]+$')

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

    def CheckText(self, val, immediate = False):
        if val == '':
            result = self.empty
        elif immediate and val == '+':
            result = True
        else:
            if self.pause:
                if matcherp.match(val) == None:
                    result = False
                else:
                    result = True
            else:
                if matcher.match(val) == None:
                    result = False
                else:
                    result = True
        return result

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
        if key < wx.WXK_SPACE or key == wx.WXK_DELETE or key > 255:
            event.Skip()
            return

        tc = self.GetWindow()
        pos = tc.GetInsertionPoint()
        val = tc.GetValue()
        newval = val[0:pos] + chr(key) + val[pos:len(val)]
        if self.CheckText(newval, immediate = True):
            event.Skip()
            return

        if not wx.Validator_IsSilent():
            wx.Bell()

        # Returning without calling even.Skip eats the event before it
        # gets to the text control
        return

