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
Settings dialog
'''

import wx
import wx.lib.rcsizer
from wx.lib.filebrowsebutton import FileBrowseButton
from wx.lib.masked.timectrl import TimeCtrl
import os
import sys
import Wammu
import Wammu.GammuSettings
import Wammu.PhoneWizard
from Wammu.Locales import ugettext as _


class Settings(wx.Dialog):
    def __init__(self, parent, config):
        wx.Dialog.__init__(self, parent, -1, _('Settings'), style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)

        # notebook
        self.notebook = wx.Notebook(self, -1)
        self.notebook_gammu = wx.Panel(self.notebook, -1)
        self.notebook_connection = wx.Panel(self.notebook, -1)
        self.notebook_messages = wx.Panel(self.notebook, -1)
        self.notebook_view = wx.Panel(self.notebook, -1)
        self.notebook_other = wx.Panel(self.notebook, -1)
        self.notebook_hacks = wx.Panel(self.notebook, -1)

        # main layout
        self.sizer = wx.lib.rcsizer.RowColSizer()

        self.sizer.AddGrowableCol(2)
        self.sizer.AddGrowableRow(1)

        self.sizer.AddSpacer(1, 1, pos=(0, 0))
        self.sizer.AddSpacer(1, 1, pos=(0, 4))

        self.sizer.Add(self.notebook, pos=(1, 1), colspan=3, flag=wx.EXPAND)

        self.sizer.Add(wx.StaticLine(self, -1), pos=(2, 1), colspan=3, flag=wx.EXPAND)

        self.button_sizer = wx.StdDialogButtonSizer()
        self.button_sizer.AddButton(wx.Button(self, wx.ID_OK))
        self.button_sizer.AddButton(wx.Button(self, wx.ID_CANCEL))
        self.button_sizer.Realize()

        self.sizer.Add(self.button_sizer, pos=(3, 1), colspan=3, flag=wx.ALIGN_RIGHT)

        self.sizer.AddSpacer(1, 1, pos=(4, 0), colspan=5)

        self.config = config
        self.gammu_config = config.gammu

        # gammu tab
        self.sizer_gammu = wx.lib.rcsizer.RowColSizer()

        self.sizer_gammu.AddGrowableCol(1)

        self.sizer_gammu.AddSpacer(1, 1, pos=(0, 0))
        r = 1

        self.editcfgpath = FileBrowseButton(
            self.notebook_gammu,
            size=(250, -1),
            labelText='',
            initialValue=config.Read('/Gammu/Gammurc', False),
            toolTip=_('Please enter here path to gammu configuration file you want to use.'),
            changeCallback=self.OnConfigChange,
            fileMode=wx.OPEN
        )
        self.sizer_gammu.Add(wx.StaticText(self.notebook_gammu, -1, _('Gammurc path')), pos=(r, 1), flag=wx.ALIGN_CENTER_VERTICAL)
        self.sizer_gammu.Add(self.editcfgpath, pos=(r, 2), flag=wx.EXPAND)
        r += 1

        self.sizer_gammu.Add(wx.StaticText(self.notebook_gammu, -1, _('You can configure connection parameters on Connection tab.')), pos=(r, 1), colspan=2)
        r += 1

        self.sizer_gammu.AddSpacer(1, 1, pos=(r, 3))
        r += 1

        self.editauto = wx.CheckBox(self.notebook_gammu, -1, _('Automatically connect to phone on startup'))
        self.editauto.SetToolTipString(_('Whether you want application automatically connect to phone when it is started.'))
        self.editauto.SetValue(config.Read('/Wammu/AutoConnect') == 'yes')
        self.sizer_gammu.Add(self.editauto, pos=(r, 1), colspan=2)
        r += 1

        self.editdebug = wx.CheckBox(self.notebook_gammu, -1, _('Show debug log'))
        self.editdebug.SetToolTipString(_('Show debug information on error output.'))
        self.editdebug.SetValue(config.Read('/Debug/Show') == 'yes')
        self.sizer_gammu.Add(self.editdebug, pos=(r, 1), colspan=2)
        r += 1

        self.editsync = wx.CheckBox(self.notebook_gammu, -1, _('Synchronize time'))
        self.editsync.SetToolTipString(_('Synchronise time in phone with computer time while connecting.'))
        self.editsync.SetValue(config.ReadBool('/Gammu/SyncTime'))
        self.sizer_gammu.Add(self.editsync, pos=(r, 1), colspan=2)
        r += 1

        self.editinfo = wx.CheckBox(self.notebook_gammu, -1, _('Startup information'))
        self.editinfo.SetToolTipString(_('Display startup on phone (not supported by all models).'))
        self.editinfo.SetValue(config.ReadBool('/Gammu/StartInfo'))
        self.sizer_gammu.Add(self.editinfo, pos=(r, 1), colspan=2)
        r += 1

        if sys.platform != 'win32':
            # locking not available on windoze
            self.editlock = wx.CheckBox(self.notebook_gammu, -1, _('Lock device'))
            self.editlock.SetToolTipString(_('Whether to lock device in /var/lock. On some systems you might lack privileges to do so.'))
            self.editlock.SetValue(config.ReadBool('/Gammu/LockDevice'))
            self.sizer_gammu.Add(self.editlock, pos=(r, 1), colspan=2)
            r += 1

        self.sizer_gammu.AddSpacer(1, 1, pos=(r, 3))

        # size gammu tab
        self.notebook_gammu.SetAutoLayout(True)
        self.notebook_gammu.SetSizer(self.sizer_gammu)
        self.sizer_gammu.Fit(self.notebook_gammu)
        self.sizer_gammu.SetSizeHints(self.notebook_gammu)

        # connection tab
        self.sizer_connection = wx.lib.rcsizer.RowColSizer()

        self.sizer_connection.AddGrowableCol(1)

        self.sizer_connection.AddSpacer(1, 1, pos=(0, 0))
        r = 1

        lst, choices = config.gammu.GetConfigList()
        self.editsection = wx.Choice(self.notebook_connection, choices=choices, size=(250, -1))
        section = config.ReadInt('/Gammu/Section')
        for i in range(len(lst)):
            if lst[i]['Id'] == section:
                self.editsection.SetSelection(i)
                break
        self.sizer_connection.Add(wx.StaticText(self.notebook_connection, -1, _('Phone connection')), pos=(r, 1), rowspan=2, flag=wx.ALIGN_CENTER_VERTICAL)
        self.sizer_connection.Add(self.editsection, pos=(r, 2))
        self.Bind(wx.EVT_CHOICE, self.OnConnectionChange, self.editsection)
        r += 1

        self.addsection = wx.Button(self.notebook_connection, wx.ID_ADD)
        self.sizer_connection.Add(self.addsection, pos=(r, 2), flag=wx.EXPAND)
        r += 1

        self.sizer_connection.AddSpacer(1, 1, pos=(r, 3))
        r += 1

        self.editname = wx.TextCtrl(self.notebook_connection, -1, '', size=(250, -1))
        self.editname.SetToolTipString(_('Name for this configuration.'))
        self.sizer_connection.Add(wx.StaticText(self.notebook_connection, -1, _('Name')), pos=(r, 1), flag=wx.ALIGN_CENTER_VERTICAL)
        self.sizer_connection.Add(self.editname, pos=(r, 2))
        r += 1

        self.editdev = wx.ComboBox(self.notebook_connection, -1, '', choices=Wammu.Data.Devices, size=(150, -1))
        self.editdev.SetToolTipString(_('Device, where your phone is connected.'))
        self.sizer_connection.Add(wx.StaticText(self.notebook_connection, -1, _('Device')), pos=(r, 1), flag=wx.ALIGN_CENTER_VERTICAL)
        self.sizer_connection.Add(self.editdev, pos=(r, 2), flag=wx.ALIGN_RIGHT | wx.EXPAND)
        r += 1

        self.editconn = wx.ComboBox(self.notebook_connection, -1, '', choices=Wammu.Data.Connections, size=(150, -1))
        self.editconn.SetToolTipString(_('Connection which your phone understands, check Gammu documentation for connection details.'))
        self.sizer_connection.Add(wx.StaticText(self.notebook_connection, -1, _('Connection')), pos=(r, 1), flag=wx.ALIGN_CENTER_VERTICAL)
        self.sizer_connection.Add(self.editconn, pos=(r, 2), flag=wx.ALIGN_RIGHT | wx.EXPAND)
        r += 1

        self.editmodel = wx.ComboBox(self.notebook_connection, -1, '', choices=Wammu.Data.Models, size=(150, -1))
        self.editmodel.SetToolTipString(_('Phone model, you can usually keep here auto unless you have any problems.'))
        if self.editmodel.GetValue() == '':
            self.editmodel.SetValue('auto')
        self.sizer_connection.Add(wx.StaticText(self.notebook_connection, -1, _('Model')), pos=(r, 1), flag=wx.ALIGN_CENTER_VERTICAL)
        self.sizer_connection.Add(self.editmodel, pos=(r, 2), flag=wx.ALIGN_RIGHT | wx.EXPAND)
        r += 1

        # Initialise above fields
        self.OnConnectionChange()

        self.sizer_connection.AddSpacer(1, 1, pos=(r, 3))

        # size connection tab
        self.notebook_connection.SetAutoLayout(True)
        self.notebook_connection.SetSizer(self.sizer_connection)
        self.sizer_connection.Fit(self.notebook_connection)
        self.sizer_connection.SetSizeHints(self.notebook_connection)

        # messages tab
        self.sizer_messages = wx.lib.rcsizer.RowColSizer()

        self.sizer_messages.AddGrowableCol(1)

        self.sizer_messages.AddSpacer(1, 1, pos=(0, 0))
        r = 1

        v = config.ReadInt('/Message/ScaleImage')
        self.editscale = wx.SpinCtrl(
            self.notebook_messages,
            -1,
            str(v),
            style=wx.SP_WRAP | wx.SP_ARROW_KEYS,
            min=1, max=20,
            initial=v,
            size=(150, -1)
        )
        self.editscale.SetToolTipString(_('Whether images in messages should be scaled when displayed. This is usually good idea as they are pretty small.'))
        self.sizer_messages.Add(wx.StaticText(self.notebook_messages, -1, _('Scale images')), pos=(r, 1))
        self.sizer_messages.Add(self.editscale, pos=(r, 2))
        r += 1

        self.editformat = wx.CheckBox(self.notebook_messages, -1, _('Attempt to reformat text'))
        self.editformat.SetToolTipString(_('If you get sometimes "compressed" messages likeTHIStext, you should be interested in this choice.'))
        self.editformat.SetValue(config.Read('/Message/Format') == 'yes')
        self.sizer_messages.Add(self.editformat, pos=(r, 1), colspan=2)
        r += 1

        # options for new message
        self.new_message_panel = wx.Panel(self.notebook_messages, -1)
        self.sizer_messages.Add(self.new_message_panel, pos=(r, 1), colspan=2, flag=wx.EXPAND)
        r += 1

        self.sizer_message_new = wx.StaticBoxSizer(wx.StaticBox(self.new_message_panel, -1, _('Default options for new message')), wx.HORIZONTAL)
        self.new_message_panel_2 = wx.Panel(self.new_message_panel, -1)
        self.sizer_message_new.Add(self.new_message_panel_2, 1, wx.EXPAND, 0)

        self.sizer_message_new_2 = wx.lib.rcsizer.RowColSizer()

        self.sizer_message_new_2.AddGrowableCol(1)

        r2 = 0

        self.editconcat = wx.CheckBox(self.new_message_panel_2, -1, _('Concatenated'))
        self.editconcat.SetToolTipString(_('Create concatenated message, what allows to send longer messages.'))
        self.editconcat.SetValue(config.Read('/Message/Concatenated') == 'yes')
        self.sizer_message_new_2.Add(self.editconcat, pos=(r2, 0), colspan=2)
        r2 += 1

        self.editunicode = wx.CheckBox(self.new_message_panel_2, -1, _('Create unicode message'))
        self.editunicode.SetToolTipString(_('Unicode messages can contain national and other special characters, check this if you use non latin-1 characters. Your messages will require more space, so you can write less characters into single message.'))
        self.editunicode.SetValue(config.Read('/Message/Unicode') == 'yes')
        self.sizer_message_new_2.Add(self.editunicode, pos=(r2, 0), colspan=2)
        r2 += 1

        self.editreport = wx.CheckBox(self.new_message_panel_2, -1, _('Request delivery report by default'))
        self.editreport.SetToolTipString(_('Check to request delivery report for message.'))
        self.editreport.SetValue(config.Read('/Message/DeliveryReport') == 'yes')
        self.sizer_message_new_2.Add(self.editreport, pos=(r2, 0), colspan=2)
        r2 += 1

        self.edit16bit = wx.CheckBox(self.new_message_panel_2, -1, _('Use 16bit Id'))
        self.edit16bit.SetToolTipString(_('Use 16 bit Id inside message. This is safe for most cases.'))
        self.edit16bit.SetValue(config.Read('/Message/16bitId') == 'yes')
        self.sizer_message_new_2.Add(self.edit16bit, pos=(r2, 0), colspan=2)
        r2 += 1

        self.new_message_panel_2.SetAutoLayout(True)
        self.new_message_panel_2.SetSizer(self.sizer_message_new_2)
        self.sizer_message_new_2.Fit(self.new_message_panel_2)
        self.sizer_message_new_2.SetSizeHints(self.new_message_panel_2)

        self.new_message_panel.SetAutoLayout(True)
        self.new_message_panel.SetSizer(self.sizer_message_new)
        self.sizer_message_new.Fit(self.new_message_panel)
        self.sizer_message_new.SetSizeHints(self.new_message_panel)

        self.sizer_messages.AddSpacer(1, 1, pos=(r, 3))

        # size messages tab
        self.notebook_messages.SetAutoLayout(True)
        self.notebook_messages.SetSizer(self.sizer_messages)
        self.sizer_messages.Fit(self.notebook_messages)
        self.sizer_messages.SetSizeHints(self.notebook_messages)

        # view tab
        self.sizer_view = wx.lib.rcsizer.RowColSizer()

        self.sizer_view.AddGrowableCol(1)

        self.sizer_view.AddSpacer(1, 1, pos=(0, 0))
        r = 1

        v = config.Read('/Wammu/NameFormat')
        self.editnameformat = wx.Choice(
            self.notebook_view,
            choices=[
                _('Automatic'),
                _('Automatic starting with first name'),
                _('Automatic starting with last name'),
                _('Custom, use format string below')
            ],
            size=(250, -1)
        )
        if v == 'auto':
            self.editnameformat.SetSelection(0)
        elif v == 'auto-first-last':
            self.editnameformat.SetSelection(1)
        elif v == 'auto-last-first':
            self.editnameformat.SetSelection(2)
        elif v == 'custom':
            self.editnameformat.SetSelection(3)
        self.sizer_view.Add(wx.StaticText(self.notebook_view, -1, _('Name display format')), pos=(r, 1))
        self.sizer_view.Add(self.editnameformat, pos=(r, 2), flag=wx.EXPAND)
        self.Bind(wx.EVT_CHOICE, self.OnNameFormatChange, self.editnameformat)
        r += 1

        v = config.Read('/Wammu/NameFormatString')
        self.editnamestring = wx.ComboBox(self.notebook_view, -1, v, choices=[
            v,
            '%(FirstName)s %(LastName)s (%(Company)s)',
            '%(LastName)s, %(FirstName)s (%(Company)s)',
            '%(LastName)s, %(FirstName)s (%(NickName)s)',
            ])
        # l10n: The %s will be replaced by list of currently supported tags, %%(value)s should be kept intact (you can translate word value).
        self.editnamestring.SetToolTipString(
            _('Format string for name displaying. You can use %%(value)s format marks. Currently available values are: %s.') %
            'Name, FirstName, LastName, NickName, FormalName, Company'
        )
        self.sizer_view.Add(wx.StaticText(self.notebook_view, -1, _('Name format string')), pos=(r, 1), flag=wx.ALIGN_CENTER_VERTICAL)
        self.sizer_view.Add(self.editnamestring, pos=(r, 2), flag=wx.ALIGN_RIGHT | wx.EXPAND)
        r += 1

        self.sizer_view.AddSpacer(1, 1, pos=(r, 3))

        # size view tab
        self.notebook_view.SetAutoLayout(True)
        self.notebook_view.SetSizer(self.sizer_view)
        self.sizer_view.Fit(self.notebook_view)
        self.sizer_view.SetSizeHints(self.notebook_view)

        # other tab
        self.sizer_other = wx.lib.rcsizer.RowColSizer()

        self.sizer_other.AddGrowableCol(1)

        self.sizer_other.AddSpacer(1, 1, pos=(0, 0))
        r = 1

        v = config.ReadInt('/Wammu/RefreshState')
        self.editrefresh = wx.SpinCtrl(
            self.notebook_other,
            -1,
            str(v),
            style=wx.SP_WRAP | wx.SP_ARROW_KEYS,
            min=0, max=10000000,
            initial=v,
            size=(150, -1)
        )
        self.editrefresh.SetToolTipString(_('How often refresh phone state in application status bar. Enter value in miliseconds, 0 to disable.'))
        self.sizer_other.Add(wx.StaticText(self.notebook_other, -1, _('Refresh phone state')), pos=(r, 1))
        self.sizer_other.Add(self.editrefresh, pos=(r, 2))
        r += 1

        self.editconfirm = wx.CheckBox(self.notebook_other, -1, _('Confirm deleting'))
        self.editconfirm.SetToolTipString(_('Whether to ask for confirmation when deleting entries.'))
        self.editconfirm.SetValue(config.Read('/Wammu/ConfirmDelete') == 'yes')
        self.sizer_other.Add(self.editconfirm, pos=(r, 1), colspan=2)
        r += 1

        self.taskbaricon = wx.CheckBox(self.notebook_other, -1, _('Task bar icon'))
        self.taskbaricon.SetToolTipString(_('Show icon in task bar.'))
        self.taskbaricon.SetValue(config.Read('/Wammu/TaskBarIcon') == 'yes')
        self.sizer_other.Add(self.taskbaricon, pos=(r, 1), colspan=2)
        r += 1

        dtime = config.Read('/Wammu/DefaultTime')
        try:
            times = dtime.split(':')
            th = int(times[0])
            tm = int(times[1])
            ts = int(times[2])
        except:
            th = 9
            tm = 0
            ts = 0
        self.edittime = TimeCtrl(self.notebook_other, -1, fmt24hr=True)
        Wammu.Utils.FixupMaskedEdit(self.edittime)
        self.edittime.SetValue(wx.DateTimeFromHMS(th, tm, ts))
        self.edittime.SetToolTipString(_('Default time to be used for newly created time fields.'))
        self.sizer_other.Add(wx.StaticText(self.notebook_other, -1, _('Default time')), pos=(r, 1))
        self.sizer_other.Add(self.edittime, pos=(r, 2))
        r += 1

        v = config.ReadInt('/Wammu/DefaultDateOffset')
        self.editdate = wx.SpinCtrl(
            self.notebook_other,
            -1,
            str(v),
            style=wx.SP_WRAP | wx.SP_ARROW_KEYS,
            min=-10000000, max=10000000,
            initial=v,
            size=(150, -1)
        )
        self.editdate.SetToolTipString(_('Default date to be used for newly created time fields. Enter amount of days from today (1=tommorow).'))
        self.sizer_other.Add(wx.StaticText(self.notebook_other, -1, _('Default date=now + x days')), pos=(r, 1))
        self.sizer_other.Add(self.editdate, pos=(r, 2))
        r += 1

        v = config.ReadInt('/Wammu/DefaultEntries')
        self.editentries = wx.SpinCtrl(
            self.notebook_other,
            -1,
            str(v),
            style=wx.SP_WRAP | wx.SP_ARROW_KEYS,
            min=0, max=20,
            initial=v,
            size=(150, -1)
        )
        self.editentries.SetToolTipString(_('How many entries will be shown in newly created item.'))
        self.sizer_other.Add(wx.StaticText(self.notebook_other, -1, _('Entries for new item')), pos=(r, 1))
        self.sizer_other.Add(self.editentries, pos=(r, 2))
        r += 1

        lst = ['Auto']
        lst += Wammu.Data.InternationalPrefixes
        self.editprefix = wx.ComboBox(self.notebook_other, -1, config.Read('/Wammu/PhonePrefix'), choices=lst, size=(150, -1))
        self.editprefix.SetToolTipString(_('Prefix for non international phone numbers.'))
        self.sizer_other.Add(wx.StaticText(self.notebook_other, -1, _('Number prefix')), pos=(r, 1))
        self.sizer_other.Add(self.editprefix, pos=(r, 2))
        r += 1

        self.sizer_other.AddSpacer(1, 1, pos=(r, 3))

        # size other tab
        self.notebook_other.SetAutoLayout(True)
        self.notebook_other.SetSizer(self.sizer_other)
        self.sizer_other.Fit(self.notebook_other)
        self.sizer_other.SetSizeHints(self.notebook_other)

        # hacks tab
        self.sizer_hacks = wx.lib.rcsizer.RowColSizer()

        self.sizer_hacks.AddGrowableCol(1)

        self.sizer_hacks.AddSpacer(1, 1, pos=(0, 0))
        r = 1

        v = config.ReadInt('/Hacks/MaxEmptyGuess')
        self.editmaxemptyguess = wx.SpinCtrl(
            self.notebook_hacks,
            -1,
            str(v),
            style=wx.SP_WRAP | wx.SP_ARROW_KEYS,
            min=0, max=10000000,
            initial=v,
            size=(150, -1)
        )
        self.editmaxemptyguess.SetToolTipString(_('Applies only when Wammu can not find proper count of entries to read. This number limits how many empty entries will be read before reading will be stopped.'))
        self.sizer_hacks.Add(wx.StaticText(self.notebook_hacks, -1, _('Maximal empty entries if total is guessed')), pos=(r, 1))
        self.sizer_hacks.Add(self.editmaxemptyguess, pos=(r, 2))
        r += 1

        v = config.ReadInt('/Hacks/MaxEmptyKnown')
        self.editmaxemptyknown = wx.SpinCtrl(
            self.notebook_hacks,
            -1,
            str(v),
            style=wx.SP_WRAP | wx.SP_ARROW_KEYS,
            min=0, max=10000000,
            initial=v,
            size=(150, -1)
        )
        self.editmaxemptyknown.SetToolTipString(_('In case phone reports wrongly number of entries, Wammu would try to read infinitely or till error. This number limits how many empty entries will be read before reading will be stopped.'))
        self.sizer_hacks.Add(wx.StaticText(self.notebook_hacks, -1, _('Maximal empty entries if total is known')), pos=(r, 1))
        self.sizer_hacks.Add(self.editmaxemptyknown, pos=(r, 2))
        r += 1

        self.sizer_hacks.AddSpacer(1, 1, pos=(r, 3))

        # size hacks tab
        self.notebook_hacks.SetAutoLayout(True)
        self.notebook_hacks.SetSizer(self.sizer_hacks)
        self.sizer_hacks.Fit(self.notebook_hacks)
        self.sizer_hacks.SetSizeHints(self.notebook_hacks)

        # add pages to notebook
        self.notebook.AddPage(self.notebook_gammu, _('Gammu'))
        self.notebook.AddPage(self.notebook_connection, _('Connection'))
        self.notebook.AddPage(self.notebook_messages, _('Messages'))
        self.notebook.AddPage(self.notebook_view, _('View'))
        self.notebook.AddPage(self.notebook_other, _('Other'))
        self.notebook.AddPage(self.notebook_hacks, _('Hacks'))

        # size main layout
        self.SetAutoLayout(True)
        self.SetSizer(self.sizer)
        self.sizer.Fit(self)
        self.sizer.SetSizeHints(self)

        # workaround, when sizers don't set correct size
        sz = self.GetSize()
        if sz.y < 150:
            self.SetSize((400, 400))

        # Intialise fields
        self.OnNameFormatChange()

        # event handlers
        self.Bind(wx.EVT_BUTTON, self.Okay, id=wx.ID_OK)
        self.Bind(wx.EVT_BUTTON, self.AddPhone, id=wx.ID_ADD)

    def OnNameFormatChange(self, evt=None):
        selection = self.editnameformat.GetSelection()
        if selection < 0:
            selection = 0
        if selection == 3:
            self.editnamestring.Enable(True)
        else:
            self.editnamestring.Enable(False)

    def OnConnectionChange(self, evt=None):
        selection = self.editsection.GetSelection()
        if selection < 0:
            selection = 0
        lst, choices = self.gammu_config.GetConfigList()
        if len(lst) == 0:
            self.editdev.Enable(False)
            self.editmodel.Enable(False)
            self.editname.Enable(False)
            self.editconn.Enable(False)
            return

        self.editdev.Enable(True)
        self.editmodel.Enable(True)
        self.editname.Enable(True)
        self.editconn.Enable(True)
        current = lst[selection]
        gammu = self.gammu_config.GetConfig(current['Id'])
        self.editdev.SetValue(gammu['Device'])
        self.editmodel.SetValue(gammu['Model'])
        self.editname.SetValue(gammu['Name'])
        self.editconn.SetValue(gammu['Connection'])

    def OnConfigChange(self, evt=None):
        # temporarily change gammu config data
        newpath = self.editcfgpath.GetValue()
        self.gammu_config = Wammu.GammuSettings.GammuSettings(
            self.config, os.path.expanduser(newpath.encode('utf-8'))
        )
        self.RereadConfig()

    def RereadConfig(self):
        lst, choices = self.gammu_config.GetConfigList()
        self.editsection.Clear()
        for x in choices:
            self.editsection.Append(x)
        if len(choices) > 0:
            self.editsection.SetSelection(0)
        self.OnConnectionChange()

    def AddPhone(self, evt=None):
        index = self.gammu_config.FirstFree()
        result = Wammu.PhoneWizard.RunConfigureWizard(self, index)
        if result is not None:
            self.gammu_config.SetConfig(result['Position'], result['Device'], result['Connection'], result['Name'])
            self.RereadConfig()
            lst, choices = self.gammu_config.GetConfigList()
            self.editsection.SetSelection(len(lst) - 1)
            self.OnConnectionChange()

    def Okay(self, evt):
        lst, choices = self.config.gammu.GetConfigList()

        # Check whether we have some configuration
        if len(lst) == 0:
            wx.MessageDialog(
                self,
                _('You don\'t have any phone connection configured. Wammu will not be able to conect to your phone!'),
                _('No phone configured!'),
                wx.OK | wx.ICON_ERROR
            ).ShowModal()
        else:
            current = lst[self.editsection.GetSelection()]
            self.config.gammu = self.gammu_config
            self.config.gammu.SetConfig(
                current['Id'],
                self.editdev.GetValue(),
                self.editconn.GetValue(),
                self.editname.GetValue(),
                self.editmodel.GetValue()
            )
            self.config.Write('/Gammu/Gammurc', self.editcfgpath.GetValue())
            self.config.WriteInt('/Gammu/Section', current['Id'])

        self.config.WriteBool('/Gammu/SyncTime', self.editsync.GetValue())
        if sys.platform != 'win32':
            self.config.WriteBool('/Gammu/LockDevice', self.editlock.GetValue())
        self.config.WriteBool('/Gammu/StartInfo', self.editinfo.GetValue())
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
        if self.editreport.GetValue():
            value = 'yes'
        else:
            value = 'no'
        self.config.Write('/Message/DeliveryReport', value)
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
        if self.taskbaricon.GetValue():
            value = 'yes'
        else:
            value = 'no'
        self.config.Write('/Wammu/TaskBarIcon', value)
        self.config.Write('Wammu/DefaultTime', self.edittime.GetValue())
        self.config.WriteInt('/Wammu/DefaultDateOffset', self.editdate.GetValue())
        self.config.WriteInt('/Wammu/DefaultEntries', self.editentries.GetValue())
        self.config.Write('/Wammu/PhonePrefix', self.editprefix.GetValue())
        self.config.Write('/Wammu/NameFormat', self.editnamestring.GetValue())
        ind = self.editnameformat.GetSelection()
        if ind == 0:
            val = 'auto'
        elif ind == 1:
            val = 'auto-first-last'
        elif ind == 2:
            val = 'auto-last-first'
        elif ind == 3:
            val = 'custom'
        else:
            raise Exception('Invalid NameFormatString id: %d' % ind)
        self.config.Write('/Wammu/NameFormat', val)

        self.config.WriteInt('/Hacks/MaxEmptyGuess', self.editmaxemptyguess.GetValue())
        self.config.WriteInt('/Hacks/MaxEmptyKnown', self.editmaxemptyknown.GetValue())
        self.EndModal(wx.ID_OK)
