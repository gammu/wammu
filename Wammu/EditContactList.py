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
Dialog for editing phone numbers list.

Created with help of wxGlade.
'''

import os
import wx
import Wammu.Select
import Wammu.Utils
import Wammu.PhoneValidator
from Wammu.Locales import StrConv
from Wammu.Locales import ugettext as _


class EditContactList(wx.Dialog):
    def __init__(self, parent, contacts, current, *args, **kwds):
        self.contacts = contacts
        self.current = current
        kwds['style'] = wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER
        wx.Dialog.__init__(self, parent, *args, **kwds)
        self.__init_data()
        self.all_label = wx.StaticText(self, -1, _('Available contacts:'))
        self.all_contacts = wx.ListBox(self, -1, choices=self.optionslist, style=wx.LB_EXTENDED)
        self.add_button = wx.Button(self, wx.ID_ADD)
        self.delete_button = wx.Button(self, wx.ID_DELETE)
        self.current_label = wx.StaticText(self, -1, _('Current recipients:'))
        self.current_contacts = wx.ListBox(self, -1, choices=self.currentlist, style=wx.LB_EXTENDED)
        self.save_button = wx.Button(self, wx.ID_SAVEAS)
        # TODO: Load would be better
        self.load_button = wx.Button(self, wx.ID_OPEN)

        self.button_sizer = wx.StdDialogButtonSizer()
        self.button_sizer.AddButton(wx.Button(self, wx.ID_OK))
        self.button_sizer.AddButton(wx.Button(self, wx.ID_CANCEL))

        self.__set_properties()
        self.__do_layout()
        self.__bind_events()

    def __bind_events(self):
        self.Bind(wx.EVT_BUTTON, self.Add, self.add_button)
        self.Bind(wx.EVT_BUTTON, self.Delete, self.delete_button)
        self.Bind(wx.EVT_BUTTON, self.Save, self.save_button)
        self.Bind(wx.EVT_BUTTON, self.Load, self.load_button)

    def __init_data(self):
        self.numberlist = []
        self.optionslist = []

        for item in self.contacts:
            numbers = []
            texts = []
            prefix = ''
            if item['Name'] != '':
                prefix = '%s: ' % item['Name']
            for i in range(len(item['Entries'])):
                if Wammu.Utils.GetItemType(item['Entries'][i]['Type']) == 'phone':
                    numbers.append(item['Entries'][i]['Value'])
                    texts.append(StrConv('%s (%s)' % (item['Entries'][i]['Value'], item['Entries'][i]['Type'])))

            if len(numbers) == 0:
                continue

            for x in range(len(numbers)):
                self.numberlist.append(numbers[x])
                self.optionslist.append(prefix + texts[x])

        self.currentlist = Wammu.PhoneValidator.SplitNumbers(self.current)
        self.wildcard = ''
        self.wildcard += _('Contact list') + ' (*.contactlist)|*.contactlist|'
        self.wildcard += _('All files') + ' (*.*)|*.*'

    def __set_properties(self):
        self.SetTitle(_('Edit contacts list'))

    def __do_layout(self):
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        sizer_1.Add((10, 10), 0, wx.ADJUST_MINSIZE, 0)
        sizer_2 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_2.Add((10, 10), 0, wx.ADJUST_MINSIZE, 0)
        sizer_4 = wx.BoxSizer(wx.VERTICAL)
        sizer_5 = wx.BoxSizer(wx.HORIZONTAL)
        sizer_6 = wx.BoxSizer(wx.VERTICAL)
        sizer_3 = wx.BoxSizer(wx.VERTICAL)
        sizer_6.Add(self.all_label, 0, wx.BOTTOM | wx.ADJUST_MINSIZE, 5)
        sizer_6.Add(self.all_contacts, 1, wx.EXPAND | wx.ADJUST_MINSIZE, 0)
        sizer_2.Add(sizer_6, 1, wx.ALL | wx.EXPAND | wx.ADJUST_MINSIZE, 0)
        sizer_3.Add(self.add_button, 0, wx.ADJUST_MINSIZE, 0)
        sizer_3.Add((20, 20), 0, wx.EXPAND | wx.ADJUST_MINSIZE, 0)
        sizer_3.Add(self.delete_button, 0, wx.ADJUST_MINSIZE, 0)
        sizer_2.Add(sizer_3, 0, wx.ALL | wx.EXPAND | wx.ADJUST_MINSIZE, 10)
        sizer_4.Add(self.current_label, 0, wx.BOTTOM | wx.ADJUST_MINSIZE, 5)
        sizer_4.Add(self.current_contacts, 1, wx.EXPAND | wx.ADJUST_MINSIZE, 0)
        sizer_5.Add(self.save_button, 0, wx.ALL | wx.ADJUST_MINSIZE, 5)
        sizer_5.Add(self.load_button, 0, wx.ALL | wx.ADJUST_MINSIZE, 5)
        sizer_4.Add(sizer_5, 0, wx.EXPAND, 0)
        sizer_2.Add(sizer_4, 1, wx.EXPAND, 0)
        sizer_2.Add((10, 10), 0, wx.ADJUST_MINSIZE, 0)
        sizer_1.Add(sizer_2, 1, wx.EXPAND, 0)
        self.button_sizer.Realize()
        sizer_1.Add(self.button_sizer, 0, wx.ALIGN_RIGHT, 0)
        self.SetAutoLayout(True)
        self.SetSizer(sizer_1)
        sizer_1.Fit(self)
        sizer_1.SetSizeHints(self)
        self.Layout()

    def GetNumbers(self):
        return ' '.join(self.currentlist)

    def Add(self, evt=None):
        index = self.all_contacts.GetSelections()
        if index == wx.NOT_FOUND:
            return
        for i in index:
            newone = self.numberlist[i]
            if newone not in self.currentlist:
                self.currentlist.append(newone)
                self.current_contacts.Append(newone)

    def Delete(self, evt=None):
        index = self.current_contacts.GetSelections()
        if index == wx.NOT_FOUND:
            return
        for i in reversed(index):
            del self.currentlist[i]
            self.current_contacts.Delete(i)

    def Save(self, evt=None):
        dlg = wx.FileDialog(
            self,
            _('Load contacts from file'),
            os.getcwd(),
            '',
            self.wildcard,
            wx.SAVE | wx.OVERWRITE_PROMPT | wx.CHANGE_DIR
        )
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            try:
                data = file(path, 'w')
                for line in self.currentlist:
                    data.write('%s\n' % line)
                data.close()
            except IOError:
                wx.MessageDialog(
                    self,
                    _('Selected file "%s" could not be written.') % path,
                    _('File can not be created!'),
                    wx.OK | wx.ICON_ERROR
                ).ShowModal()

    def Load(self, evt=None):
        dlg = wx.FileDialog(
            self,
            _('Load contacts from file'),
            os.getcwd(),
            '',
            self.wildcard,
            wx.OPEN | wx.CHANGE_DIR
        )
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            try:
                newlist = []
                data = file(path, 'r')
                for line in data:
                    newlist.append(line.strip())
                data.close()
                self.currentlist = newlist
                self.current_contacts.Set(newlist)
            except IOError:
                wx.MessageDialog(
                    self,
                    _('Selected file "%s" was not found, no data read.') % path,
                    _('File not found!'),
                    wx.OK | wx.ICON_ERROR
                ).ShowModal()
