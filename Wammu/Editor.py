# -*- coding: UTF-8 -*-
# Wammu - Phone manager
# Copyright (c) 2003 - 2004 Michal Čihař
#
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 2 of the License.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for
# more details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc., 59 Temple
# Place, Suite 330, Boston, MA 02111-1307 USA
'''
Item editors
'''

import wx
try:
    # wxPython 2.4
    from wxPython.utils import wxDateTimeFromDMY as DateTimeFromDMY, wxDateTime_Today as DateTime_Today
except ImportError:
    try:
        # wxPython 2.5.1
        from wx.misc import DateTimeFromDMY, DateTime_Today
    except ImportError:
        # wxPython 2.5.2
        from wx import DateTimeFromDMY, DateTime_Today

import wx.calendar
try:
    from wx.lib.timectrl import TimeCtrl
except ImportError:
    # wxPython 2.5.2
    from wx.lib.masked.timectrl import TimeCtrl
import Wammu.wxcomp.popupctl
import sys
import datetime
import time
import Wammu
import Wammu.Data
import Wammu.Utils
import Wammu.Select
import Wammu.PhoneValidator
from Wammu.Utils import StrConv, UnicodeConv, Str_ as _

def TextToTime(txt):
    hms = txt.split(':')
    return datetime.time(int(hms[0]), int(hms[1]), int(hms[2]))

def TextToDate(txt):
    ymd = txt.split('-')
    return datetime.date(int(ymd[0]), int(ymd[1]), int(ymd[2]))

def TimeToText(time):
    try:
        try:
            time = time.time()
        except:
            pass
        return time.isoformat()
    except:
        #FIXME: configurable
        return '9:00:00'

def DateToText(date):
    try:
        try:
            date = date.date()
        except:
            pass
        return date.isoformat()
    except:
        #FIXME: configurable
        return str(datetime.datetime.fromtimestamp(time.time() + 24*60*60).date())

class DateControl(Wammu.wxcomp.popupctl.wxPopupControl):
    """
    Date editor heavilly based on wxPython example - wxPopupControl.py
    """
    def __init__(self, parent, value):
        Wammu.wxcomp.popupctl.wxPopupControl.__init__(self, parent, value)

        self.win = wx.Window(self,-1,pos = (0,0),style = 0)
        self.cal = wx.calendar.CalendarCtrl(self.win,-1,pos = (0,0))

        bz = self.cal.GetBestSize()
        self.win.SetSize(bz)

        # This method is needed to set the contents that will be displayed
        # in the popup
        self.SetPopupContent(self.win)

        # Event registration for date selection
        wx.calendar.EVT_CALENDAR_DAY(self.cal,self.cal.GetId(),self.OnCalSelected)

    # Method called when a day is selected in the calendar
    def OnCalSelected(self,evt):
        self.PopDown()
        date = self.cal.GetDate()

        # Format the date that was selected for the text part of the control
        self.SetValue('%04d-%02d-%02d' % (date.GetYear(),
                                          date.GetMonth()+1,
                                          date.GetDay()))
        evt.Skip()

    # Method overridden from wxPopupControl
    # This method is called just before the popup is displayed
    # Use this method to format any controls in the popup
    def FormatContent(self):
        # I parse the value in the text part to resemble the correct date in
        # the calendar control
        txtValue = self.GetValue()
        dmy = txtValue.split('-')
        didSet = False
        if len(dmy) == 3:
            d = int(dmy[2])
            m = int(dmy[1]) - 1
            y = int(dmy[0])
            if d > 0 and d < 31:
                if m >= 0 and m < 12:
                    if y > 1000:
                        date = DateTimeFromDMY(d,m,y)
                        self.cal.SetDate(date)
                        didSet = True
        if not didSet:
            time = DateTime_Today()
            self.cal.SetDate()


class DateTimeEdit(wx.Panel):
    """
    Generic class for static text with some edit control.
    """
    def __init__(self, parent, value):
        wx.Panel.__init__(self, parent, -1)
        self.sizer = wx.FlexGridSizer(1, 3, 2, 2)
        self.sizer.AddGrowableCol(1)
        try:
            val = str(value.time())
        except:
            #FIXME: configurable
            val = '9:00:00'
        self.timeed = TimeCtrl( self, -1, val, fmt24hr=True)
        try:
            val = str(value.date())
        except:
            #FIXME: configurable
            val = str(datetime.datetime.fromtimestamp(time.time() + 24*60*60).date())
        self.dateed = DateControl(self, val)
        self.SetValue(value)
        self.sizer.AddMany([
            (self.dateed, 0, wx.EXPAND),
            (self.timeed, 0, wx.EXPAND),
            ])
        self.sizer.Fit(self)
        self.SetAutoLayout(True)
        self.SetSizer(self.sizer)

    def GetValue(self):
        txtdate = self.dateed.GetValue()
        ymd = txtdate.split('-')
        txttime = self.timeed.GetValue()
        hms = txttime.split(':')
        return datetime.datetime(int(ymd[0]), int(ymd[1]), int(ymd[2]), int(hms[0]), int(hms[1]), int(hms[2]))

    def SetValue(self, value):
        try:
            val = str(value.time())
        except:
            #FIXME: configurable
            val = '9:00:00'
        self.timeed.SetValue(val)
        try:
            val = str(value.date())
        except:
            #FIXME: configurable
            val = str(datetime.datetime.fromtimestamp(time.time() + 24*60*60).date())
        self.dateed.SetValue(val)


class ContactEdit(wx.Panel):
    """
    Contact editor
    """
    def __init__(self, parent, val, values):
        wx.Panel.__init__(self, parent, -1)
        self.values = values
        self.sizer = wx.FlexGridSizer(1, 3, 2, 2)
        self.sizer.AddGrowableCol(1)
        self.edit = wx.SpinCtrl(self, -1, str(val), style = wx.SP_WRAP|wx.SP_ARROW_KEYS, min = 0, max = 10000, initial = val, size = (200, -1))
        self.txt = wx.StaticText(self, -1, self.GetText(val))
        self.btn = wx.Button(self, -1, _('...'), style = wx.BU_EXACTFIT)
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

class TextEdit(wx.Panel):
    """
    Generic class for static text with some edit control.
    """
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, -1)

    def PostInit(self, text, control):
        self.sizer = wx.FlexGridSizer(1, 3, 2, 2)
        self.sizer.AddGrowableCol(1)
        self.control = control
        self.sizer.AddMany([
            (wx.StaticText(self, -1, text),     0, wx.EXPAND),
            (10,10),
            (self.control,                      0, wx.EXPAND),
            ])
        self.sizer.Fit(self)
        self.SetAutoLayout(True)
        self.SetSizer(self.sizer)

    def GetValue(self):
        return self.control.GetValue()

    def SetValue(self, value):
        return self.control.SetValue(value)


class TextCombo(TextEdit):
    """
    Text + Combo edit control
    """
    def __init__(self, parent, text, value, choices):
        TextEdit.__init__(self, parent)
        self.PostInit(text, wx.ComboBox(self, -1, value, choices = choices, style = wx.CB_READONLY))

class TextNumber(TextEdit):
    """
    Text + Spin edit control
    """
    def __init__(self, parent, text, value, min = 1, max = sys.maxint):
        TextEdit.__init__(self, parent)
        self.PostInit(text, wx.SpinCtrl(self, -1, str(value), style = wx.SP_WRAP|wx.SP_ARROW_KEYS , min = min, max = max, initial = value))

class OneEdit(wx.Panel):
    """
    Text + Combo + editor for type specified by combo value
    """
    def __init__(self, parent, text, type, choices, value, values):
        wx.Panel.__init__(self, parent, -1)
        self.values = values
        self.sizer = wx.FlexGridSizer(1, 4, 2, 2)
        self.sizer.AddGrowableCol(1)
        self.sizer.AddGrowableCol(2)
        self.sizer.AddGrowableCol(3)
        self.text = wx.StaticText(self, -1, text, size = (20, -1))
        self.combo = wx.ComboBox(self, -1, type, choices = choices, style = wx.CB_READONLY, size = (180, -1))
        self.sizer.AddMany([
            (self.text,   0, wx.ALL),
            (self.combo,  1, wx.ALL),
            ])
        self.CreateEdit(type, value)
        self.sizer.Fit(self)
        self.SetAutoLayout(True)
        self.SetSizer(self.sizer)
        wx.EVT_TEXT(self.combo, self.combo.GetId(), self.OnChange)

    def CreateEdit(self, newtype, value = None):
        if value == None and hasattr(self, 'edit'):
            value = self.edit.GetValue()

        if hasattr(self, 'type'):
            oldt = Wammu.Utils.GetItemType(self.type)
        else:
            oldt = ''
        newt = Wammu.Utils.GetItemType(newtype)

        self.type = newtype
        if oldt == newt:
            return

        self.sizer.Remove(2)
        self.sizer.Remove(3)
        if hasattr(self, 'edit'):
            del self.edit

        if hasattr(self, 'edit2'):
            del self.edit2

        self.edit2 = wx.StaticText(self, -1, '')
        if newt == 'text' or newt == None:
            self.edit = wx.TextCtrl(self, -1, StrConv(value), size = (200, -1))
        elif newt == 'phone':
            self.edit = wx.TextCtrl(self, -1, StrConv(value), size = (200, -1), validator = Wammu.PhoneValidator.PhoneValidator(pause = True))
        elif newt == 'bool':
            try:
                val = bool(value)
            except:
                val = False
            self.edit = wx.CheckBox(self, -1, '', size = (200, -1))
            self.edit.SetValue(val)
        elif newt == 'contact':
            try:
                val = int(value)
            except:
                val = 0
            lst = [] + self.values['contact']['ME']
            self.edit = ContactEdit(self, val, lst)
        elif newt == 'id':
            v = hex(value)
            if v[-1] == 'L':
                v = v[:-1]
            self.edit = wx.TextCtrl(self, -1, v, size = (200, -1))
        elif newt == 'category' or newt == 'number':
            try:
                val = int(value)
            except:
                val = 0
            self.edit = wx.SpinCtrl(self, -1, str(val), style = wx.SP_WRAP|wx.SP_ARROW_KEYS, min = -10000, max = 10000, initial = val, size = (200, -1))
        elif newt == 'datetime':
            self.edit = TimeCtrl( self, -1, TimeToText(value), fmt24hr=True)
            self.edit2 = DateControl(self, DateToText(value))
        elif newt == 'date':
            self.edit = DateControl(self, DateToText(value))
        else:
            print 'warning: creating TextCtrl for %s' % newt
            self.edit = wx.TextCtrl(self, -1, StrConv(value), size = (200, -1))

        self.sizer.AddMany([
            (self.edit,   1, wx.EXPAND|wx.ALIGN_LEFT|wx.ALL),
            (self.edit2,  1, wx.EXPAND|wx.ALL)
            ])

    def OnChange(self, evt):
        self.CreateEdit(evt.GetString())
        self.sizer.SetSizeHints(self)

    def GetValue(self):
        t = Wammu.Utils.GetItemType(self.type)
        if t == 'date':
            return TextToDate(self.edit.GetValue())
        elif t == 'datetime':
            return datetime.datetime.combine(TextToDate(self.edit2.GetValue()), TextToTime(self.edit.GetValue()))
        elif t == 'id':
            return int(self.edit.GetValue(), 16)
        elif t in ['contact', 'bool', 'category', 'number']:
            return int(self.edit.GetValue())
        elif t in ['phone', 'text']:
            return UnicodeConv(self.edit.GetValue())
        else:
            return self.edit.GetValue()

    def GetType(self):
        return self.combo.GetValue()

    def Validate(self):
        if Wammu.Utils.GetItemType(self.type) == 'datetime':
            v = self.edit2.GetValidator()
            if v != None:
                val2 = v.Validate(self)
            else:
                val2 = True
        else:
            val2 = True
        v = self.edit.GetValidator()
        if v != None:
            return v.Validate(self) and val2
        else:
            return val2

class OkCancelMore(wx.Panel):
    """
    OK + Cancel + More buttons
    """
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, -1)
        self.sizer = wx.FlexGridSizer(1, 4, 2, 2)

        self.ok = wx.Button(self, wx.ID_OK, _('OK'))
        self.cancel = wx.Button(self, wx.ID_CANCEL, _('Cancel'))
        self.more = wx.Button(self, -1, _('More'))

        self.sizer.AddMany([
            (self.ok,       0, wx.EXPAND | wx.ALL),
            (self.cancel,   0, wx.EXPAND | wx.ALL),
            (self.more,     0, wx.EXPAND | wx.ALL),
            ])

        self.sizer.Fit(self)
        self.SetAutoLayout(True)
        self.SetSizer(self.sizer)


class GenericEditor(wx.Dialog):
    """
    Generic editor customised further by it's descendants
    """
    def __init__(self, parent, cfg, values, entry, internalname, name, location, type, typedefault, typename, typevalues, itemtypes ):
        if entry == {}:
            title = _('Creating new %s') % name
            wasempty = True
        else:
            title = _('Editing %s %s') % (name, location)
            wasempty = False

        wx.Dialog.__init__(self, parent, -1, title, style = wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)
        self.entry = entry
        self.values = values
        self.type = type
        self.cfg = cfg
        self.internalname = internalname
        self.itemtypes = itemtypes
        self.sizer = wx.FlexGridSizer(3, 1, 2, 2)
        self.sizer.AddGrowableCol(0)
        list = []
        if wasempty:
            entry['Location'] = 0
            entry[type] = typedefault

        self.locationedit = TextNumber(self,  _('Location (0 = auto):'), entry['Location'], 0)
        self.typeedit = TextCombo(self, typename, entry[type], typevalues)

        wx.EVT_TEXT(self.typeedit.control, self.typeedit.control.GetId(), self.OnTypeChange)

        list.append((self.locationedit,   0, wx.EXPAND|wx.ALL, 2))
        list.append((self.typeedit,   0, wx.EXPAND|wx.ALL, 2))
        self.edits = []
        x = 0
        if wasempty:
            for x in range(3):
                e = OneEdit(self, '%d.' % (x + 1), '', self.itemtypes + [''] , '', self.values)
                self.edits.append(e)
                list.append((e, 0, wx.EXPAND|wx.ALL, 2))
        else:
            for i in entry['Entries']:
                e = OneEdit(self, '%d.' % (x + 1), i['Type'], self.itemtypes + [''] , i['Value'], self.values)
                self.edits.append(e)
                list.append((e, 0, wx.EXPAND|wx.ALL, 2))
                x = x + 1

        self.buttons = OkCancelMore(self)
        list.append((self.buttons, 0, wx.ALL|wx.ALIGN_CENTER, 2))

        self.sizer.AddMany(list)
        self.sizer.Fit(self)
        self.SetAutoLayout(True)
        self.SetSizer(self.sizer)
        wx.EVT_BUTTON(self, wx.ID_OK, self.Okay)
        wx.EVT_BUTTON(self, self.buttons.more.GetId(), self.More)

    def OnTypeChange(self, evt):
        self.locationedit.SetValue(0)

    def More(self, evt):
        self.sizer.Remove(len(self.edits) + 2)

        e = OneEdit(self, '%d.' % (len(self.edits) + 1), '', self.itemtypes + [''] , '', self.values)
        self.edits.append(e)

        self.sizer.AddMany([
            (e, 0, wx.EXPAND|wx.ALL,2),
            (self.buttons, 0, wx.ALL|wx.ALIGN_CENTER, 2)
            ])
        self.sizer.Fit(self)

    def Okay(self, evt):
        # FIXME: why it needed to call validators directly?
        for e in self.edits:
            if not e.Validate():
                return

        v = []
        for x in self.edits:
            t = x.GetType()
            if t != '':
                v.append({'Type' : t, 'Value' : x.GetValue()})

        self.entry['Entries'] = v
        self.entry[self.type] = self.typeedit.GetValue()
        self.entry['Location'] = self.locationedit.GetValue()
        self.EndModal(wx.ID_OK)

class ContactEditor(GenericEditor):
    def __init__(self, parent, cfg, values, entry):
        if entry == {}:
            location = ''
        else:
            location = '%s:%d' % (entry['MemoryType'], entry['Location'])
        GenericEditor.__init__(self, parent, cfg, values, entry, 'contact',  _('contact'), location, 'MemoryType', 'SM', _('Memory type'), Wammu.Data.ContactMemoryTypes, Wammu.Data.MemoryValueTypes)

class CalendarEditor(GenericEditor):
    def __init__(self, parent, cfg, values, entry):
        if entry == {}:
            location = ''
        else:
            location = '%d' % entry['Location']
        GenericEditor.__init__(self, parent, cfg, values, entry, 'calendar',  _('calendar event'), location, 'Type', 'MEETING', _('Event type'), Wammu.Data.CalendarTypes, Wammu.Data.CalendarValueTypes)

class TodoEditor(GenericEditor):
    def __init__(self, parent, cfg, values, entry):
        if entry == {}:
            location = ''
        else:
            location = '%d' % entry['Location']
        GenericEditor.__init__(self, parent, cfg, values, entry, 'todo',  _('todo item'), location, 'Priority', 'Medium', _('Priority'), Wammu.Data.TodoPriorities, Wammu.Data.TodoValueTypes)
