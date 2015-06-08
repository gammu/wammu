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
Wizard helper classes
'''

import wx
import wx.wizard
import Wammu.Paths


class SimplePage(wx.wizard.PyWizardPage):
    """
    Simple wizard page with unlimited rows of text.
    """
    def __init__(self, parent, titletext, bodytext=None, detailtexts=None):
        wx.wizard.PyWizardPage.__init__(self, parent)
        self.parent = parent
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self.sizer)
        title = wx.StaticText(self, -1, titletext)
        title.SetFont(wx.Font(18, wx.SWISS, wx.NORMAL, wx.BOLD))
        self.sizer.Add(title, 0, wx.ALIGN_CENTRE | wx.ALL, 5)
        self.sizer.Add(wx.StaticLine(self, -1), 0, wx.EXPAND | wx.ALL, 5)
        self.prev = None
        self.next = None
        if bodytext is not None:
            body = wx.StaticText(self, -1, bodytext)
            body.Wrap(400)
            self.sizer.Add(body, 0, wx.ALL, 5)
        if detailtexts is not None:
            for row in detailtexts:
                detail = wx.StaticText(self, -1, row)
                detail.Wrap(400)
                self.sizer.Add(detail, 0, wx.ALL, 5)

    def SetNext(self, next):
        self.next = next

    def SetPrev(self, prev):
        self.prev = prev

    def GetNext(self):
        return self.next

    def GetPrev(self):
        return self.prev

    def Activated(self, evt):
        """
        Executed when page is being activated.
        """
        return

    def Blocked(self, evt):
        """
        Executed when page is about to be switched. Switching can be
        blocked by returning True.
        """
        return False

    def Cancel(self, evt):
        """
        Executed when wizard is about to be canceled. Canceling can be
        blocked by returning False.
        """
        return True


class ChoicePage(SimplePage):
    """
    Page offering choice of several values and allowing to automatically
    select next page according to choice.
    """
    def __init__(self, parent, title, text, choices, helps, nexts=None,
                 nonetext='', extratext=None):
        Wammu.Wizard.SimplePage.__init__(self, parent, title, extratext)
        self.type_rb = wx.RadioBox(
            self, -1, text,
            size=(400, -1),
            majorDimension=1,
            choices=choices
        )
        self.texts = helps
        self.nexts = nexts
        self.Bind(wx.EVT_RADIOBOX, self.OnTypeChange, self.type_rb)
        self.sizer.Add(self.type_rb, 0, wx.ALL, 5)
        try:
            self.body = wx.StaticText(self, -1, self.texts[0])
        except:
            self.body = wx.StaticText(self, -1, nonetext)
        self.body.Wrap(400)
        self.sizer.Add(self.body, 0, wx.ALL, 5)

    def OnTypeChange(self, evt):
        try:
            self.body.SetLabel(self.texts[evt.GetSelection()])
            self.body.Wrap(400)
        except:
            self.body.SetLabel('')
        self.sizer.Fit(self)

    def GetType(self):
        return self.type_rb.GetSelection()

    def GetNext(self):
        if self.nexts is None or len(self.nexts) == 0:
            return self.next
        return self.nexts[self.type_rb.GetSelection()]


class InputPage(SimplePage):
    """
    Page offering text control input.
    """
    def __init__(self, parent, title, text, choices=None, help=''):
        Wammu.Wizard.SimplePage.__init__(self, parent, title, text)
        if type(choices) == str:
            self.edit = wx.TextCtrl(self, -1, choices, size=(300, -1))
        else:
            self.edit = wx.ComboBox(
                self, -1, '', choices=choices, size=(300, -1)
            )
        self.sizer.Add(self.edit, 0, wx.ALL, 5)
        self.body = wx.StaticText(self, -1, help)
        self.body.Wrap(400)
        self.sizer.Add(self.body, 0, wx.ALL, 5)


class MultiInputPage(SimplePage):
    """
    Page offering several text control inputs.
    """
    def __init__(self, parent, title, texts, choices):
        Wammu.Wizard.SimplePage.__init__(self, parent, title)
        self.edits = {}
        for i in range(len(texts)):
            body = wx.StaticText(self, -1, texts[i])
            body.Wrap(400)
            self.sizer.Add(body, 0, wx.ALL, 5)
            self.edits[i] = wx.ComboBox(
                self, -1, '', choices=choices[i], size=(300, -1)
            )
            self.sizer.Add(self.edits[i], 0, wx.ALL, 5)


class TextPage(SimplePage):
    """
    Page offering big text control.
    """
    def __init__(self, parent, title, text):
        Wammu.Wizard.SimplePage.__init__(self, parent, title, text)
        self.edit = wx.TextCtrl(
            self, -1, '', style=wx.TE_MULTILINE | wx.TE_READONLY
        )
        self.sizer.Add(self.edit, 1, wx.ALL | wx.EXPAND, 5)
