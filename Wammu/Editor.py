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
Item editors
'''

import wx
from wx import DateTimeFromDMY, DateTime_Today
import wx.calendar
import wx.lib.masked.timectrl
from wx.lib.masked import Ctrl as maskedCtrl
from Wammu.Paths import MiscPath
import datetime
import time
import Wammu
import Wammu.Data
import Wammu.Utils
import Wammu.Select
import Wammu.PhoneValidator
from Wammu.Locales import StrConv, UnicodeConv, ugettext as _


def TextToTime(txt, config):
    hms = txt.split(':')
    try:
        return datetime.time(int(hms[0]), int(hms[1]), int(hms[2]))
    except UnicodeEncodeError:
        hms = config.Read('/Wammu/DefaultTime').split(':')
        return datetime.time(int(hms[0]), int(hms[1]), int(hms[2]))

def TextToDate(txt):
    dmy = txt.split('.')
    try:
        return datetime.date(int(dmy[2]), int(dmy[1]), int(dmy[0]))
    except UnicodeEncodeError:
        return datetime.date.today()

def TimeToText(time, config):
    try:
        try:
            time = time.time()
        except:
            pass
        return time.isoformat()
    except:
        return config.Read('/Wammu/DefaultTime')

def DateToText(date, config):
    try:
        try:
            date = date.date()
        except:
            pass
        return date.strftime('%d.%m.%Y')
    except:
        return datetime.datetime.fromtimestamp(time.time() + 24*60*60*config.ReadInt('/Wammu/DefaultDateOffset')).date().strftime('%d.%m.%Y')

class TimeCtrl(wx.lib.masked.timectrl.TimeCtrl):
    def Validate(self):
        return self.IsValid(self.GetValue())

class CalendarPopup(wx.PopupTransientWindow):
    def __init__(self, parent):
        wx.PopupTransientWindow.__init__(self, parent, wx.SIMPLE_BORDER)
        self.cal = wx.calendar.CalendarCtrl(self, -1, pos=(0, 0), style=wx.calendar.CAL_SEQUENTIAL_MONTH_SELECTION)
        sz = self.cal.GetBestSize()
        self.SetSize(sz)

class DateControl(wx.Panel):
    def __init__(self, parent, value):
        wx.Panel.__init__(self, parent, -1)

        self.sizer = wx.FlexGridSizer(1, 2)
        self.sizer.AddGrowableCol(0)
        self.textCtrl = maskedCtrl(self, -1, autoformat='EUDATEDDMMYYYY.', validRequired=True, emptyInvalid=True)
        Wammu.Utils.FixupMaskedEdit(self.textCtrl)
        self.textCtrl.SetValue(value)
        self.bCtrl = wx.BitmapButton(self, -1, wx.Bitmap(MiscPath('downarrow')))
        self.sizer.AddMany([
            (self.textCtrl, 1, wx.EXPAND),
            (self.bCtrl, 1, wx.EXPAND),
            ])
        self.sizer.Fit(self)
        self.SetAutoLayout(True)
        self.SetSizer(self.sizer)
        wx.EVT_BUTTON(self.bCtrl, self.bCtrl.GetId(), self.OnButton)
        wx.EVT_SET_FOCUS(self, self.OnFocus)

    def GetValidator(self):
        return self.textCtrl.GetValidator()

    def Validate(self):
        return self.textCtrl.Validate()

    def OnFocus(self, evt):
        self.textCtrl.SetFocus()
        evt.Skip()

    def OnButton(self, evt):
        self.pop = CalendarPopup(self)
        txtValue = self.GetValue()
        dmy = txtValue.split('.')
        didSet = False
        if len(dmy) == 3:
            d = int(dmy[0])
            m = int(dmy[1]) - 1
            y = int(dmy[2])
            if d > 0 and d < 31:
                if m >= 0 and m < 12:
                    if y > 1000:
                        self.pop.cal.SetDate(DateTimeFromDMY(d, m, y))
                        didSet = True
        if not didSet:
            self.pop.cal.SetDate(DateTime_Today())

        pos = self.ClientToScreen((0, 0))
        display_size = wx.GetDisplaySize()
        popup_size = self.pop.GetSize()
        control_size = self.GetSize()

        pos.x -= (popup_size.x - control_size.x) / 2
        if pos.x + popup_size.x > display_size.x:
            pos.x = display_size.x - popup_size.x
        if pos.x < 0:
            pos.x = 0

        pos.y += control_size.height
        if pos.y + popup_size.y > display_size.y:
            pos.y = display_size.y - popup_size.y
        if pos.y < 0:
            pos.y = 0
        self.pop.MoveXY(pos.x, pos.y)
        wx.calendar.EVT_CALENDAR_DAY(self, self.pop.cal.GetId(), self.OnCalSelected)
        self.pop.Popup()

    def Enable(self, flag):
        wx.PyControl.Enable(self, flag)
        self.textCtrl.Enable(flag)
        self.bCtrl.Enable(flag)

    def SetValue(self, value):
        self.textCtrl.SetValue(value)

    def GetValue(self):
        return self.textCtrl.GetValue()

    def OnCalSelected(self, evt):
        date = self.pop.cal.GetDate()
        self.SetValue('%02d.%02d.%04d' % (
            date.GetDay(),
            date.GetMonth() + 1,
            date.GetYear()))
        self.pop.Dismiss()
        evt.Skip()

class ContactEdit(wx.Panel):
    """
    Contact editor
    """
    def __init__(self, parent, val, values):
        wx.Panel.__init__(self, parent, -1)
        self.values = values
        self.sizer = wx.FlexGridSizer(1, 3, 2, 2)
        self.sizer.AddGrowableCol(1)
        self.edit = wx.SpinCtrl(
            self,
            -1,
            str(val),
            style=wx.SP_WRAP | wx.SP_ARROW_KEYS,
            min=0, max=10000,
            initial=val,
            size=(200, -1)
        )
        self.txt = wx.StaticText(self, -1, self.GetText(val))
        self.btn = wx.Button(self, -1, '...', style=wx.BU_EXACTFIT)
        self.sizer.AddMany([
            (self.edit,                     0, wx.EXPAND),
            (self.txt,                      1, wx.EXPAND),
            (self.btn,                      0, wx.EXPAND),
            ])
        wx.EVT_TEXT(self.edit, self.edit.GetId(), self.OnChange)
        wx.EVT_BUTTON(self.btn, self.btn.GetId(), self.OnContacts)
        self.sizer.Fit(self)
        self.SetAutoLayout(True)
        self.SetSizer(self.sizer)

    def OnChange(self, evt):
        self.txt.SetLabel(self.GetText(self.edit.GetValue()))
        self.sizer.Fit(self)
#        self.sizer.SetSizeHints(self)

    def OnContacts(self, evt):
        i = Wammu.Select.SelectContact(self, self.values)
        if i != -1:
            self.SetValue(i)

    def GetText(self, val):
        if val < 1:
            return _('None')
        else:
            l = Wammu.Utils.SearchLocation(self.values, val)
            if l == -1:
                return _('Unknown')
            else:
                return self.values[l]['Name']

    def GetValue(self):
        return self.edit.GetValue()

    def SetValue(self, value):
        return self.edit.SetValue(value)


class GenericEditor(wx.Dialog):
    """
    Generic editor customised further by it's descendants
    """
    def __init__(self, parent, cfg, values, entry, internalname, name, location, type, typename, typevalues, itemtypes ):
        if entry == {}:
            title = _('Creating new %s') % name
            self.wasempty = True
        else:
            title = _('Editing %(name)s %(location)s') % {
                'name': name,
                'location': location
            }
            self.wasempty = False

        wx.Dialog.__init__(self, parent, -1, title, style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)
        self.rows = 0
        self.entry = entry
        self.values = values
        self.type = type
        self.cfg = cfg
        self.internalname = internalname
        self.itemtypes = itemtypes
        self.sizer = wx.GridBagSizer(5, 5)
        self.sizer.SetCols(6)
        self.sizer.AddGrowableCol(2)
        self.sizer.AddGrowableCol(5)
        if self.wasempty:
            entry['Location'] = 0
            entry[type] = self.cfg.Read('/Defaults/Type-%s-%s' % (internalname, type))

        self.sizer.Add(wx.StaticText(self, -1, _('Location (0=auto):')), (0, 0), (1, 4))
        # there used to be sys.maxint on following line, but it's too large on amd64 (or there is bug in wxPython)
        self.locationedit = wx.SpinCtrl(
            self,
            -1,
            str(entry['Location']),
            style=wx.SP_WRAP | wx.SP_ARROW_KEYS,
            min=0, max=2147483647,
            initial=entry['Location']
        )
        self.sizer.Add(self.locationedit, (0, 4), (1, 4))

        self.sizer.Add(wx.StaticText(self, -1, typename), (1, 0), (1, 4))
        self.typeedit = wx.ComboBox(self, -1, entry[type], choices=typevalues, style=wx.CB_READONLY)
        self.sizer.Add(self.typeedit, (1, 4), (1, 4))

        self.rowoffset = 2

        self.Bind(wx.EVT_TEXT, self.OnTypeChange, self.typeedit)

        self.edits = {}
        self.types = {}
        self.fulltypes = {}
        x = 0
        if self.wasempty:
            for x in range(self.cfg.ReadInt('/Wammu/DefaultEntries')):
                entrytype = self.cfg.Read('/Defaults/Entry-%s-%d' % (self.internalname, x))
                if entrytype != '':
                    self.AddEdit(x, {'Type': entrytype, 'Value': '', 'VoiceTag': 0, 'AddError': 0})
                else:
                    self.AddEdit(x)
        else:
            for i in range(len(entry['Entries'])):
                self.AddEdit(i, entry['Entries'][i])

        self.more = wx.Button(self, wx.ID_ADD)
        self.more.SetToolTipString(_('Add one more field.'))
        self.button_sizer = wx.StdDialogButtonSizer()
        self.button_sizer.AddButton(wx.Button(self, wx.ID_OK))
        self.button_sizer.AddButton(wx.Button(self, wx.ID_CANCEL))
        self.button_sizer.SetNegativeButton(self.more)
        self.button_sizer.Realize()
        self.Bind(wx.EVT_BUTTON, self.Okay, id=wx.ID_OK)
        self.Bind(wx.EVT_BUTTON, self.More, self.more)

        self.SetAutoLayout(True)
        self.SetSizer(self.sizer)

        self.AddButtons()

    def AddButtons(self):
        row = self.rowoffset + self.rows + 1
        self.sizer.Add(self.button_sizer, pos=(row, 1), span=wx.GBSpan(colspan=7), flag=wx.ALIGN_RIGHT)
        self.sizer.Fit(self)
        self.sizer.SetSizeHints(self)
        self.sizer.Layout()

    def RemoveButtons(self):
        self.sizer.Detach(self.button_sizer)

    def AddEdit(self, row, value=None):
        if value is None:
            value = {
                'Type': '',
                'Value': ''
            }
        self.rows += 1
        self.sizer.Add(wx.StaticText(self, -1, '%d.' % (row + 1), size=(20, -1)), (row + self.rowoffset, 0))
        combo = wx.ComboBox(self, -1, value['Type'], choices=self.itemtypes + [''], style=wx.CB_READONLY, size=(180, -1))
        combo.row = row
        self.sizer.Add(combo, (row + self.rowoffset, 1), (1, 3))
        self.Bind(wx.EVT_TEXT, self.OnItemTypeChange, combo)
        self.AddTypeEdit(row, value)

    def AddTypeEdit(self, row, value):
        type = Wammu.Utils.GetItemType(value['Type'])
        self.fulltypes[row] = value['Type']
        self.types[row] = type
        if type == 'text' or type is None:
            # text editor
            edit = wx.TextCtrl(self, -1, StrConv(value['Value']), size=(200, -1))
            self.sizer.Add(edit, (row + self.rowoffset, 4), (1, 4))
            self.edits[row] = [edit]
        elif type == 'phone':
            # phone editor with voice tag
            edit = wx.TextCtrl(self, -1, StrConv(value['Value']), size=(150, -1), validator=Wammu.PhoneValidator.PhoneValidator(pause=True))
            self.sizer.Add(edit, (row + self.rowoffset, 4), (1, 3))
            try:
                v = hex(value['VoiceTag'])
            except:
                v = '0x0'
            if v[-1] == 'L':
                v = v[:-1]
            edit2 = wx.TextCtrl(self, -1, v, size=(50, -1))
            self.sizer.Add(edit2, (row + self.rowoffset, 7), (1, 1))
            self.edits[row] = [edit, edit2]
        elif type == 'bool':
            # boolean
            try:
                val = bool(value['Value'])
            except:
                val = False
            edit = wx.CheckBox(self, -1, '', size=(200, -1))
            edit.SetValue(val)
            self.sizer.Add(edit, (row + self.rowoffset, 4), (1, 4))
            self.edits[row] = [edit]
        elif type == 'contact':
            # contact editor
            try:
                val = int(value['Value'])
            except:
                val = 0
            edit = wx.SpinCtrl(
                self,
                -1,
                str(val),
                style=wx.SP_WRAP | wx.SP_ARROW_KEYS,
                min=0, max=10000,
                initial=val,
                size=(50, -1)
            )
            edit.row = row
            self.sizer.Add(edit, (row + self.rowoffset, 4), (1, 1))
            edit2 = wx.Button(self, -1, self.GetContactText(val), style=wx.BU_EXACTFIT, size=(150, -1))
            edit2.row = row
            self.sizer.Add(edit2, (row + self.rowoffset, 5), (1, 3))
            self.edits[row] = [edit, edit2]
            self.Bind(wx.EVT_SPINCTRL, self.OnContactSpinChange, edit)
            self.Bind(wx.EVT_BUTTON, self.OnContactButton, edit2)
        elif type == 'id':
            # ID editor
            try:
                v = hex(value['Value'])
            except:
                v = '0x0'
            if v[-1] == 'L':
                v = v[:-1]
            edit = wx.TextCtrl(self, -1, StrConv(v), size=(200, -1))
            self.sizer.Add(edit, (row + self.rowoffset, 4), (1, 4))
            self.edits[row] = [edit]
        elif type == 'category' or type == 'number':
            # number editor
            # FIXME: category should be selectable
            try:
                val = int(value['Value'])
            except:
                val = 0
            edit = wx.SpinCtrl(
                self,
                -1,
                str(val),
                style=wx.SP_WRAP | wx.SP_ARROW_KEYS,
                min=-10000, max=10000,
                initial=val,
                size=(200, -1)
            )
            self.sizer.Add(edit, (row + self.rowoffset, 4), (1, 4))
            self.edits[row] = [edit]
        elif type == 'datetime':
            # date + time editor
            edit = TimeCtrl(self, -1, fmt24hr=True)
            Wammu.Utils.FixupMaskedEdit(edit)
            edit.SetValue(TimeToText(value['Value'], self.cfg))
            self.sizer.Add(edit, (row + self.rowoffset, 4), (1, 2))
            edit2 = DateControl(self, DateToText(value['Value'], self.cfg))
            self.sizer.Add(edit2, (row + self.rowoffset, 6), (1, 2))
            self.edits[row] = [edit, edit2]
        elif type == 'date':
            # date editor
            edit = DateControl(self, DateToText(value['Value'], self.cfg))
            self.sizer.Add(edit, (row + self.rowoffset, 4), (1, 4))
            self.edits[row] = [edit]
        else:
            print 'warning: creating TextCtrl for %s' % type
            edit = wx.TextCtrl(self, -1, StrConv(value['Value']), size=(200, -1))
            self.sizer.Add(edit, (row + self.rowoffset, 4), (1, 4))
            self.edits[row] = [edit]
        self.sizer.Fit(self)
        self.sizer.SetSizeHints(self)
        self.sizer.Layout()

    def OnContactSpinChange(self, evt):
        row = evt.GetEventObject().row
        self.edits[row][1].SetLabel(self.GetContactText(evt.GetInt()))

    def OnContactButton(self, evt):
        row = evt.GetEventObject().row
        val = Wammu.Select.SelectContact(self, [] + self.values['contact']['ME'])
        if val != -1:
            self.edits[row][0].SetValue(val)
            self.edits[row][1].SetLabel(self.GetContactText(val))

    def GetContactText(self, val):
        if val < 1:
            return _('None')
        else:
            l = Wammu.Utils.SearchLocation(self.values['contact']['ME'], val)
            if l == -1:
                return _('Unknown')
            else:
                return self.values['contact']['ME'][l]['Name']

    def DelTypeEdit(self, row):
        for x in self.edits[row]:
            if x is not None:
                self.sizer.Detach(x)
                x.Destroy()
        self.edits[row] = [None]

    def GetTypeEditValue(self, row):
        if self.types[row] == 'date':
            return TextToDate(self.edits[row][0].GetValue())
        elif self.types[row] == 'datetime':
            return datetime.datetime.combine(TextToDate(self.edits[row][1].GetValue()), TextToTime(self.edits[row][0].GetValue(), self.cfg))
        elif self.types[row] == 'id':
            return int(self.edits[row][0].GetValue(), 16)
        elif self.types[row] in ['contact', 'bool', 'category', 'number']:
            return int(self.edits[row][0].GetValue())
        elif self.types[row] in ['phone', 'text']:
            return UnicodeConv(self.edits[row][0].GetValue())
        else:
            return self.edits[row][0].GetValue()

    def GetTypeEditVoiceTag(self, row):
        if self.types[row] == 'phone':
            return int(self.edits[row][1].GetValue(), 16)
        return 0

    def OnItemTypeChange(self, evt):
        row = evt.GetEventObject().row
        typestring = evt.GetString()
        val = self.GetTypeEditValue(row)
        self.DelTypeEdit(row)
        self.AddTypeEdit(row, {'Type': typestring, 'Value': val})

    def OnTypeChange(self, evt):
        self.locationedit.SetValue(0)

    def More(self, evt):
        self.RemoveButtons()
        self.AddEdit(self.rows)
        self.AddButtons()

    def Okay(self, evt):
        if not self.Validate():
            return

        v = []
        for row in range(self.rows):
            t = self.fulltypes[row]
            if t != '':
                v.append({
                    'Type': t,
                    'Value': self.GetTypeEditValue(row),
                    'VoiceTag': self.GetTypeEditVoiceTag(row)
                })

        self.entry['Entries'] = v
        self.entry[self.type] = self.typeedit.GetValue()
        self.entry['Location'] = self.locationedit.GetValue()

        # Remember default type
        if self.wasempty:
            self.cfg.Write(
                '/Defaults/Type-%s-%s' % (self.internalname, self.type),
                self.entry[self.type]
            )

        self.EndModal(wx.ID_OK)

class ContactEditor(GenericEditor):
    def __init__(self, parent, cfg, values, entry):
        if entry == {}:
            location = ''
        else:
            location = '%s:%d' % (entry['MemoryType'], entry['Location'])
        GenericEditor.__init__(self, parent, cfg, values, entry, 'contact',  _('contact'), location, 'MemoryType', _('Memory type'), Wammu.Data.ContactMemoryTypes, Wammu.Data.MemoryValueTypes)

class CalendarEditor(GenericEditor):
    def __init__(self, parent, cfg, values, entry):
        if entry == {}:
            location = ''
        else:
            location = '%d' % entry['Location']
        GenericEditor.__init__(self, parent, cfg, values, entry, 'calendar',  _('calendar event'), location, 'Type', _('Event type'), Wammu.Data.CalendarTypes, Wammu.Data.CalendarValueTypes)

class TodoEditor(GenericEditor):
    def __init__(self, parent, cfg, values, entry):
        if entry == {}:
            location = ''
        else:
            location = '%d' % entry['Location']
        GenericEditor.__init__(self, parent, cfg, values, entry, 'todo',  _('todo item'), location, 'Priority', _('Priority'), Wammu.Data.TodoPriorities, Wammu.Data.TodoValueTypes)

    def Okay(self, evt):
        self.entry['Type'] = 'MEMO'
        GenericEditor.Okay(self, evt)
