# -*- coding: UTF-8 -*-
# Wammu - Phone manager
# Copyright (c) 2003 - 2005 Michal Čihař
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
# this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
'''
Settings dialog
'''

import wx
import wx.lib.rcsizer
import sys
import Wammu
from Wammu.Utils import Str_ as _
try:
    from wx.lib.timectrl import TimeCtrl
except ImportError:
    # wxPython 2.5.2
    from wx.lib.masked.timectrl import TimeCtrl

class Settings(wx.Dialog):
    def __init__(self, parent, config):
        wx.Dialog.__init__(self, parent, -1, _('Settings'), style = wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)

        # notebook
        self.notebook= wx.Notebook(self, -1)
        self.notebook_connection = wx.Panel(self.notebook, -1)
        self.notebook_messages = wx.Panel(self.notebook, -1)
        self.notebook_other = wx.Panel(self.notebook, -1)

        # main layout
        self.sizer = wx.lib.rcsizer.RowColSizer()

        self.sizer.AddGrowableCol(2)
        self.sizer.AddGrowableRow(1)

        self.sizer.AddSpacer(1, 1, pos = (0, 0))
        self.sizer.AddSpacer(1, 1, pos = (0, 4))

        self.sizer.Add(self.notebook, pos = (1, 1), colspan = 3, flag = wx.EXPAND)

        self.sizer.Add(wx.StaticLine(self, -1), pos = (2, 1), colspan = 3, flag = wx.EXPAND)

        button = wx.Button(self, wx.ID_OK, _('&OK'))
        button.SetDefault()
        self.sizer.Add(button, pos = (3, 1))
        self.sizer.Add(wx.Button(self, wx.ID_CANCEL, _('&Cancel')), pos = (3, 3), flag = wx.ALIGN_RIGHT)

        self.sizer.AddSpacer(1, 1, pos = (4, 0), colspan = 5)

        self.config = config

        # connection tab
        self.sizer_connection = wx.lib.rcsizer.RowColSizer()

        self.sizer_connection.AddGrowableCol(1)

        self.sizer_connection.AddSpacer(1, 1, pos = (0, 0))
        r = 1

        self.editdev = wx.ComboBox(self.notebook_connection, -1, config.Read('/Gammu/Device', Wammu.Data.Devices[0]), choices = Wammu.Data.Devices, size = (150, -1))
        self.editdev.SetToolTipString(_('Device, where your phone is connected.'))
        self.sizer_connection.Add(wx.StaticText(self.notebook_connection, -1, _('Device')), pos = (r, 1))
        self.sizer_connection.Add(self.editdev, pos = (r, 2))
        r += 1

        self.editconn = wx.ComboBox(self.notebook_connection, -1, config.Read('/Gammu/Connection', Wammu.Data.Connections[0]), choices = Wammu.Data.Connections, size = (150, -1))
        self.editconn.SetToolTipString(_('Connection which your phone understands, check Gammu documentation for connection details.'))
        self.sizer_connection.Add(wx.StaticText(self.notebook_connection, -1, _('Connection')), pos = (r, 1))
        self.sizer_connection.Add(self.editconn, pos = (r, 2))
        r += 1

        self.editmodel = wx.ComboBox(self.notebook_connection, -1, config.Read('/Gammu/Model', Wammu.Data.Models[0]), choices = Wammu.Data.Models, size = (150, -1))
        self.editmodel.SetToolTipString(_('Phone model, you can usually keep here auto unless you have any problems.'))
        if self.editmodel.GetValue() == '':
            self.editmodel.SetValue('auto')
        self.sizer_connection.Add(wx.StaticText(self.notebook_connection, -1, _('Model')), pos = (r, 1))
        self.sizer_connection.Add(self.editmodel, pos = (r, 2))
        r += 1

        if sys.platform != 'win32':
            # locking not available on windoze
            self.editlock = wx.CheckBox(self.notebook_connection, -1, _('Lock device'))
            self.editlock.SetToolTipString(_('Whether to lock device in /var/lock. On some systems you might lack privileges to do so.'))
            self.editlock.SetValue(config.Read('/Gammu/LockDevice', 'no') == 'yes')
            self.sizer_connection.Add(self.editlock, pos = (r, 1), colspan = 2)
            r += 1

        self.editauto = wx.CheckBox(self.notebook_connection, -1, _('Automatically connect to phone on startup'))
        self.editauto.SetToolTipString(_('Whether you want application automatically connect to phone when it is started.'))
        self.editauto.SetValue(config.Read('/Wammu/AutoConnect', 'no') == 'yes')
        self.sizer_connection.Add(self.editauto, pos = (r, 1), colspan = 2)
        r += 1

        self.sizer_connection.AddSpacer(1, 1, pos = (r, 3))

        # size connection tab
        self.notebook_connection.SetAutoLayout(True)
        self.notebook_connection.SetSizer(self.sizer_connection)
        self.sizer_connection.Fit(self.notebook_connection)
        self.sizer_connection.SetSizeHints(self.notebook_connection)

        # messages tab
        self.sizer_messages = wx.lib.rcsizer.RowColSizer()

        self.sizer_messages.AddGrowableCol(1)

        self.sizer_messages.AddSpacer(1, 1, pos = (0, 0))
        r = 1

        v = config.ReadInt('/Message/ScaleImage', 1)
        self.editscale = wx.SpinCtrl(self.notebook_messages, -1, str(v), style = wx.SP_WRAP|wx.SP_ARROW_KEYS, min = 1, max = 20, initial = v, size = (150, -1))
        self.editscale.SetToolTipString(_('Whether images in messages should be scaled when displayed. This is usually good idea as they are pretty small.'))
        self.sizer_messages.Add(wx.StaticText(self.notebook_messages, -1, _('Scale images')), pos = (r, 1))
        self.sizer_messages.Add(self.editscale, pos = (r, 2))
        r += 1

        self.editformat = wx.CheckBox(self.notebook_messages, -1, _('Attempt to reformat text'))
        self.editformat.SetToolTipString(_('If you get sometimes "compressed" messages likeTHIStext, you should be interested in this choice.'))
        self.editformat.SetValue(config.Read('/Message/Format', 'yes') == 'yes')
        self.sizer_messages.Add(self.editformat, pos = (r, 1), colspan = 2)
        r += 1

        # options for new message
        self.new_message_panel = wx.Panel(self.notebook_messages, -1)
        self.sizer_messages.Add(self.new_message_panel, pos = (r, 1), colspan = 2, flag = wx.EXPAND)
        r += 1

        self.sizer_message_new = wx.StaticBoxSizer(wx.StaticBox(self.new_message_panel, -1, 'Default options for new message'), wx.HORIZONTAL)
        self.new_message_panel_2 = wx.Panel(self.new_message_panel, -1)
        self.sizer_message_new.Add(self.new_message_panel_2, 1, wx.EXPAND, 0)

        self.sizer_message_new_2 = wx.lib.rcsizer.RowColSizer()

        self.sizer_message_new_2.AddGrowableCol(1)

        r2 = 0

        self.editconcat = wx.CheckBox(self.new_message_panel_2, -1, _('Concatenated'))
        self.editconcat.SetToolTipString(_('Create concatenated message, what allows to send longer messages.'))
        self.editconcat.SetValue(config.Read('/Message/Concatenated', 'yes') == 'yes')
        self.sizer_message_new_2.Add(self.editconcat, pos = (r2, 0), colspan = 2)
        r2 += 1

        self.editunicode = wx.CheckBox(self.new_message_panel_2, -1, _('Create unicode message'))
        self.editunicode.SetToolTipString(_('Unicode messages can contain national and other special characters, check this if you use non latin-1 characters. Your messages will require more space, so you can write less characters into single message.'))
        self.editunicode.SetValue(config.Read('/Message/Unicode', 'no') == 'yes')
        self.sizer_message_new_2.Add(self.editunicode, pos = (r2, 0), colspan = 2)
        r2 += 1

        self.edit16bit = wx.CheckBox(self.new_message_panel_2, -1, _('Use 16bit Id'))
        self.edit16bit.SetToolTipString(_('Use 16 bit Id inside message. This is safe for most cases.'))
        self.edit16bit.SetValue(config.Read('/Message/16bitId', 'yes') == 'yes')
        self.sizer_message_new_2.Add(self.edit16bit, pos = (r2, 0), colspan = 2)
        r2 += 1

        self.new_message_panel_2.SetAutoLayout(True)
        self.new_message_panel_2.SetSizer(self.sizer_message_new_2)
        self.sizer_message_new_2.Fit(self.new_message_panel_2)
        self.sizer_message_new_2.SetSizeHints(self.new_message_panel_2)

        self.new_message_panel.SetAutoLayout(True)
        self.new_message_panel.SetSizer(self.sizer_message_new)
        self.sizer_message_new.Fit(self.new_message_panel)
        self.sizer_message_new.SetSizeHints(self.new_message_panel)

        self.sizer_messages.AddSpacer(1, 1, pos = (r, 3))

        # size messages tab
        self.notebook_messages.SetAutoLayout(True)
        self.notebook_messages.SetSizer(self.sizer_messages)
        self.sizer_messages.Fit(self.notebook_messages)
        self.sizer_messages.SetSizeHints(self.notebook_messages)

        # other tab
        self.sizer_other = wx.lib.rcsizer.RowColSizer()

        self.sizer_other.AddGrowableCol(1)

        self.sizer_other.AddSpacer(1, 1, pos = (0, 0))
        r = 1

        v = config.ReadInt('/Wammu/RefreshState', 5000)
        self.editrefresh = wx.SpinCtrl(self.notebook_other, -1, str(v), style = wx.SP_WRAP|wx.SP_ARROW_KEYS, min = 0, max = 10000000, initial = v, size = (150, -1))
        self.editrefresh.SetToolTipString(_('How often refresh phone state in application status bar. Enter value in miliseconds, 0 to disable.'))
        self.sizer_other.Add(wx.StaticText(self.notebook_other, -1, _('Refresh phone state')), pos = (r, 1))
        self.sizer_other.Add(self.editrefresh, pos = (r, 2))
        r += 1

        self.editsync = wx.CheckBox(self.notebook_other, -1, _('Synchronize time'))
        self.editsync.SetToolTipString(_('Synchronise time in phone with computer time while connecting.'))
        self.editsync.SetValue(config.Read('/Gammu/SyncTime', 'no') == 'yes')
        self.sizer_other.Add(self.editsync, pos = (r, 1), colspan = 2)
        r += 1

        self.editinfo = wx.CheckBox(self.notebook_other, -1, _('Startup information'))
        self.editinfo.SetToolTipString(_('Display startup on phone (not supported by all models).'))
        self.editinfo.SetValue(config.Read('/Gammu/StartInfo', 'no') == 'yes')
        self.sizer_other.Add(self.editinfo, pos = (r, 1), colspan = 2)
        r += 1

        self.editdebug = wx.CheckBox(self.notebook_other, -1, _('Show debug log'))
        self.editdebug.SetToolTipString(_('Show debug information on error output.'))
        self.editdebug.SetValue(config.Read('/Debug/Show', 'no') == 'yes')
        self.sizer_other.Add(self.editdebug, pos = (r, 1), colspan = 2)
        r += 1

        self.editconfirm = wx.CheckBox(self.notebook_other, -1, _('Confirm deleting'))
        self.editconfirm.SetToolTipString(_('Whether to ask for confirmation when deleting entries.'))
        self.editconfirm.SetValue(config.Read('/Wammu/ConfirmDelete', 'yes') == 'yes')
        self.sizer_other.Add(self.editconfirm, pos = (r, 1), colspan = 2)
        r += 1

        dtime = config.Read('Wammu/DefaultTime', '09:00:00')
        try:
            times = dtime.split(':')
            th = int(times[0])
            tm = int(times[1])
            ts = int(times[2])
        except:
            th = 9
            tm = 0
            ts = 0
        self.edittime = TimeCtrl( self.notebook_other, -1, wx.DateTimeFromHMS(th, tm, ts), fmt24hr = True)
        self.edittime.SetToolTipString(_('Default time to be used for newly created time fields.'))
        self.sizer_other.Add(wx.StaticText(self.notebook_other, -1, _('Default time')), pos = (r, 1))
        self.sizer_other.Add(self.edittime, pos = (r, 2))
        r += 1

        v = config.ReadInt('/Wammu/DefaultDateOffset', 1)
        self.editdate = wx.SpinCtrl(self.notebook_other, -1, str(v), style = wx.SP_WRAP|wx.SP_ARROW_KEYS, min = -10000000, max = 10000000, initial = v, size = (150, -1))
        self.editdate.SetToolTipString(_('Default date to be used for newly created time fields. Enter amount of days from today (1 = tommorow).'))
        self.sizer_other.Add(wx.StaticText(self.notebook_other, -1, _('Default time = now + x days')), pos = (r, 1))
        self.sizer_other.Add(self.editdate, pos = (r, 2))
        r += 1

        v = config.ReadInt('/Wammu/DefaultEntries', 3)
        self.editentries = wx.SpinCtrl(self.notebook_other, -1, str(v), style = wx.SP_WRAP|wx.SP_ARROW_KEYS, min = 0, max = 20, initial = v, size = (150, -1))
        self.editentries.SetToolTipString(_('How many entries will be shown in newly created item.'))
        self.sizer_other.Add(wx.StaticText(self.notebook_other, -1, _('Entries for new item')), pos = (r, 1))
        self.sizer_other.Add(self.editentries, pos = (r, 2))
        r += 1

        self.sizer_other.AddSpacer(1, 1, pos = (r, 3))

        # size other tab
        self.notebook_other.SetAutoLayout(True)
        self.notebook_other.SetSizer(self.sizer_other)
        self.sizer_other.Fit(self.notebook_other)
        self.sizer_other.SetSizeHints(self.notebook_other)

        # add pages to notebook
        self.notebook.AddPage(self.notebook_connection, _("Connection"))
        self.notebook.AddPage(self.notebook_messages, _("Messages"))
        self.notebook.AddPage(self.notebook_other, _("Other"))

        # size main layout
        self.SetAutoLayout(True)
        self.SetSizer(self.sizer)
        self.sizer.Fit(self)
        self.sizer.SetSizeHints(self)

        # workaround, when sizers don't set correct size
        sz = self.GetSize()
        if sz.y < 150:
            self.SetSize((400, 400))

        # event handler
        wx.EVT_BUTTON(self, wx.ID_OK, self.Okay)

    def Okay(self, evt):
        self.config.Write('/Gammu/Model', self.editmodel.GetValue())
        self.config.Write('/Gammu/Device', self.editdev.GetValue())
        self.config.Write('/Gammu/Connection', self.editconn.GetValue())
        if self.editsync.GetValue():
            value = 'yes'
        else:
            value = 'no'
        self.config.Write('/Gammu/SyncTime', value)
        if self.editlock.GetValue():
            value = 'yes'
        else:
            value = 'no'
        self.config.Write('/Gammu/LockDevice', value)
        if self.editinfo.GetValue():
            value = 'yes'
        else:
            value = 'no'
        self.config.Write('/Gammu/StartInfo', value)
        if self.editdebug.GetValue():
            value = 'yes'
        else:
            value = 'no'
        self.config.Write('/Debug/Show', value)
        if self.editauto.GetValue():
            value = 'yes'
        else:
            value = 'no'
        self.config.Write('/Wammu/AutoConnect', value)
        if self.editformat.GetValue():
            value = 'yes'
        else:
            value = 'no'
        self.config.Write('/Message/Format', value)
        if self.editconcat.GetValue():
            value = 'yes'
        else:
            value = 'no'
        self.config.Write('/Message/Concatenated', value)
        if self.editunicode.GetValue():
            value = 'yes'
        else:
            value = 'no'
        self.config.Write('/Message/Unicode', value)
        if self.edit16bit.GetValue():
            value = 'yes'
        else:
            value = 'no'
        self.config.Write('/Message/16bitId', value)
        self.config.WriteInt('/Message/ScaleImage', self.editscale.GetValue())
        self.config.WriteInt('/Wammu/RefreshState', self.editrefresh.GetValue())
        if self.editconfirm.GetValue():
            value = 'yes'
        else:
            value = 'no'
        self.config.Write('Wammu/ConfirmDelete', value)
        self.config.Write('Wammu/DefaultTime', self.edittime.GetValue())
        self.config.WriteInt('/Wammu/DefaultDateOffset', self.editdate.GetValue())
        self.config.WriteInt('/Wammu/DefaultEntries', self.editentries.GetValue())
        self.EndModal(wx.ID_OK)
