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
Main Wammu window
'''

import wx
import wx.html
import sys

import os
import datetime
import time
import copy
import tempfile
import Wammu.Webbrowser
import Wammu
import re

# We can use dbus for some fancy stuff
try:
    import dbus
    import dbus.glib
    HAVE_DBUS = True
except ImportError:
    HAVE_DBUS = False

try:
    import gammu
except SystemError as err:
    Wammu.gammu_error = err
except ImportError as err:
    Wammu.gammu_error = err

import Wammu.Events
import Wammu.Displayer
import Wammu.Browser
import Wammu.Editor
import Wammu.Error
import Wammu.Info
import Wammu.Utils
import Wammu.Logger
import Wammu.Message
import Wammu.Memory
import Wammu.Todo
import Wammu.Calendar
import Wammu.Settings
from Wammu.Paths import AppIconPath, IconPath
import wx.lib.wxpTag
import wx.lib.dialogs
import Wammu.Data
import Wammu.Composer
import Wammu.MessageDisplay
import Wammu.PhoneSearch
import Wammu.About
import Wammu.ErrorMessage
import Wammu.TalkbackDialog
import Wammu.WammuSettings
import Wammu.SMSExport
import Wammu.SMSXML
import Wammu.ContactsXML
from Wammu.Locales import StrConv, ConsoleStrConv, ugettext as _

TALKBACK_COUNT = 30
TALKBACK_DAYS = 30


def SortDataKeys(first, second):
    if first == 'info':
        return -1
    elif second == 'info':
        return 1
    return cmp(first, second)


def SortDataSubKeys(first, second):
    if first == '  ':
        return -1
    elif second == '  ':
        return 1
    return cmp(first, second)


displaydata = {}
displaydata['info'] = {}
displaydata['call'] = {}
displaydata['contact'] = {}
displaydata['message'] = {}
displaydata['todo'] = {}
displaydata['calendar'] = {}

# information
displaydata['info']['  '] = ('', _('Phone'), _('Phone Information'), 'phone', [
    {
        'Name': _('Wammu version'),
        'Value': Wammu.__version__,
        'Synced': True
    },
])
if Wammu.gammu_error is None:
    displaydata['info']['  '][4].append({
        'Name': _('Gammu version'),
        'Value': gammu.Version()[0],
        'Synced': True
    })
    displaydata['info']['  '][4].append({
        'Name': _('python-gammu version'),
        'Value': gammu.Version()[1],
        'Synced': True
    })

# calls
displaydata['call']['  '] = ('info', _('Calls'), _('All Calls'), 'call', [])
displaydata['call']['RC'] = ('call', _('Received'), _('Received Calls'), 'call-received', [])
displaydata['call']['MC'] = ('call', _('Missed'), _('Missed Calls'), 'call-missed', [])
displaydata['call']['DC'] = ('call', _('Outgoing'), _('Outgoing Calls'), 'call-outgoing', [])

# contacts
displaydata['contact']['  '] = ('info', _('Contacts'), _('All Contacts'), 'contact', [])
displaydata['contact']['SM'] = ('contact', _('SIM'), _('SIM Contacts'), 'contact-sim', [])
displaydata['contact']['ME'] = ('contact', _('Phone'), _('Phone Contacts'), 'contact-phone', [])

# contacts
displaydata['message']['  '] = ('info', _('Messages'), _('All Messages'), 'message', [])
displaydata['message']['Read'] = ('message', _('Read'), _('Read Messages'), 'message-read', [])
displaydata['message']['UnRead'] = ('message', _('Unread'), _('Unread Messages'), 'message-unread', [])
displaydata['message']['Sent'] = ('message', _('Sent'), _('Sent Messages'), 'message-sent', [])
displaydata['message']['UnSent'] = ('message', _('Unsent'), _('Unsent Messages'), 'message-unsent', [])

# todos
displaydata['todo']['  '] = ('info', _('Todos'), _('All Todo Items'), 'todo', [])

# calendar
displaydata['calendar']['  '] = ('info', _('Calendar'), _('All Calendar Events'), 'calendar', [])


## Create a new frame class, derived from the wxPython Frame.
class WammuFrame(wx.Frame):

    def __init__(self, parent, id):
        self.cfg = Wammu.WammuSettings.WammuConfig()
        Wammu.configuration = self.cfg
        if self.cfg.HasEntry('/Main/X') and self.cfg.HasEntry('/Main/Y'):
            pos = wx.Point(self.cfg.ReadInt('/Main/X'), self.cfg.ReadInt('/Main/Y'))
        else:
            pos = wx.DefaultPosition
        size = wx.Size(self.cfg.ReadInt('/Main/Width'), self.cfg.ReadInt('/Main/Height'))

        wx.Frame.__init__(self, parent, id, 'Wammu', pos, size, wx.DEFAULT_FRAME_STYLE)

        if sys.platform == 'win32':
            img = wx.Image(AppIconPath('wammu'), wx.BITMAP_TYPE_ICO)
        else:
            img = wx.Image(AppIconPath('wammu'), wx.BITMAP_TYPE_PNG)

        self.icon = wx.EmptyIcon()
        self.icon.CopyFromBitmap(wx.BitmapFromImage(img))

        if self.icon.GetWidth() == 16 and self.icon.GetHeight() == 16:
            self.icon16 = self.icon
        else:
            img.Rescale(16, 16)
            self.icon16 = wx.EmptyIcon()
            self.icon16.CopyFromBitmap(wx.BitmapFromImage(img))

        self.SetIcon(self.icon)

        self.CreateStatusBar(2)
        self.SetStatusWidths([-1, 400])

        # Associate some events with methods of this class
        wx.EVT_CLOSE(self, self.CloseWindow)
        Wammu.Events.EVT_PROGRESS(self, self.OnProgress)
        Wammu.Events.EVT_SHOW_MESSAGE(self, self.OnShowMessage)
        Wammu.Events.EVT_LINK(self, self.OnLink)
        Wammu.Events.EVT_DATA(self, self.OnData)
        Wammu.Events.EVT_SHOW(self, self.OnShow)
        Wammu.Events.EVT_EDIT(self, self.OnEdit)
        Wammu.Events.EVT_SEND(self, self.OnSend)
        Wammu.Events.EVT_CALL(self, self.OnCall)
        Wammu.Events.EVT_MESSAGE(self, self.OnMessage)
        Wammu.Events.EVT_DUPLICATE(self, self.OnDuplicate)
        Wammu.Events.EVT_REPLY(self, self.OnReply)
        Wammu.Events.EVT_DELETE(self, self.OnDelete)
        Wammu.Events.EVT_BACKUP(self, self.OnBackup)
        Wammu.Events.EVT_EXCEPTION(self, self.OnException)

        self.splitter = wx.SplitterWindow(self, -1)
        il = wx.ImageList(16, 16)

        self.tree = wx.TreeCtrl(self.splitter)
        self.tree.AssignImageList(il)

        self.treei = {}
        self.values = {}

        keys = displaydata.keys()
        keys.sort(SortDataKeys)
        for type in keys:
            self.treei[type] = {}
            self.values[type] = {}
            subkeys = displaydata[type].keys()
            subkeys.sort(SortDataSubKeys)
            for subtype in subkeys:
                self.values[type][subtype] = displaydata[type][subtype][4]
                if displaydata[type][subtype][0] == '':
                    self.treei[type][subtype] = self.tree.AddRoot(
                        displaydata[type][subtype][1],
                        il.Add(wx.Bitmap(IconPath(displaydata[type][subtype][3]))))
                else:
                    self.treei[type][subtype] = self.tree.AppendItem(
                        self.treei[displaydata[type][subtype][0]]['  '],
                        displaydata[type][subtype][1],
                        il.Add(wx.Bitmap(IconPath(displaydata[type][subtype][3]))))

        for type in keys:
            self.tree.Expand(self.treei[type]['  '])

        wx.EVT_TREE_SEL_CHANGED(self, self.tree.GetId(), self.OnTreeSel)

        # common border sizes (Gnome HIG)
        self.separatorHalf = 3
        self.separatorNormal = 6
        self.separatorTwice = 12

        # right frame
        self.rightsplitter = wx.SplitterWindow(self.splitter, -1)
        self.rightwin = wx.Panel(self.rightsplitter, -1)
        self.rightwin.sizer = wx.BoxSizer(wx.VERTICAL)

        # title text
        self.righttitle = wx.StaticText(self.rightwin, -1, 'Wammu')
        self.rightwin.sizer.Add(
            self.righttitle,
            0,
            wx.LEFT | wx.ALL | wx.EXPAND,
            self.separatorNormal
        )

        # line
        self.rightwin.sizer.Add(wx.StaticLine(self.rightwin, -1), 0, wx.EXPAND)

        # search input
        self.searchpanel = wx.Panel(self.rightwin, -1)
        self.searchpanel.sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.searchpanel.sizer.Add(wx.StaticText(self.searchpanel, -1, _('Search: ')), 0, wx.LEFT | wx.CENTER)
        self.searchinput = wx.TextCtrl(self.searchpanel, -1)
        self.searchinput.SetToolTipString(_('Enter text to search for, please note that search type is selected next to this field. Matching is done over all fields.'))
        self.searchpanel.sizer.Add(self.searchinput, 1, wx.CENTER | wx.ALIGN_CENTER_VERTICAL)
        self.searchchoice = wx.Choice(self.searchpanel, choices=[_('Text'), _('Regexp'), _('Wildcard')])
        self.searchchoice.SetToolTipString(_('Select search type'))
        self.searchchoice.SetSelection(self.cfg.ReadInt('/Defaults/SearchType'))
        self.searchpanel.sizer.Add(self.searchchoice, 0, wx.LEFT | wx.CENTER | wx.EXPAND, self.separatorNormal)
        self.searchclear = wx.Button(self.searchpanel, wx.ID_CLEAR)
        self.searchpanel.sizer.Add(self.searchclear, 0, wx.LEFT | wx.CENTER | wx.EXPAND, self.separatorNormal)
        self.searchpanel.SetSizer(self.searchpanel.sizer)
        self.rightwin.sizer.Add(self.searchpanel, 0, wx.LEFT | wx.ALL | wx.EXPAND, self.separatorNormal)

        self.Bind(wx.EVT_CHOICE, self.OnSearch, self.searchchoice)
        self.Bind(wx.EVT_TEXT, self.OnSearch, self.searchinput)
        self.Bind(wx.EVT_BUTTON, self.ClearSearch, self.searchclear)

        # item browser
        self.browser = Wammu.Browser.Browser(self.rightwin, self, self.cfg)
        self.rightwin.sizer.Add(self.browser, 1, wx.EXPAND)
        self.rightwin.SetSizer(self.rightwin.sizer)

        # values displayer
        self.content = Wammu.Displayer.Displayer(self.rightsplitter, self)

        self.splitter.SplitVertically(self.tree, self.rightsplitter, self.cfg.ReadInt('/Main/Split'))
        self.rightsplitter.SplitHorizontally(self.rightwin, self.content, self.cfg.ReadInt('/Main/SplitRight'))

        # initial content
        self.content.SetContent('<font size=+1><b>%s</b></font>' % (_('Welcome to Wammu %s') % Wammu.__version__))

        # Prepare the menu bar
        self.menuBar = wx.MenuBar()

        menu1 = wx.Menu()
        menu1.Append(100, _('&Write data'), _('Write data (except messages) to file.'))
        menu1.Append(101, _('W&rite message'), _('Write messages to file.'))
        menu1.Append(102, _('&Read data'), _('Read data (except messages) from file (does not import to the phone).'))
        menu1.Append(103, _('R&ead messages'), _('Read messages from file (does not import to the phone).'))
        menu1.AppendSeparator()
        menu1.Append(150, _('&Phone wizard'), _('Search for phone or configure it using guided wizard.'))
        menu1.Append(151, _('Se&ttings'), _('Change Wammu settings.'))
        menu1.AppendSeparator()
        menu1.Append(199, '%s\tCtrl+Q' % _('E&xit'), _('Terminate Wammu.'))
        # Add menu to the menu bar
        self.menuBar.Append(menu1, _('&Wammu'))

        menu2 = wx.Menu()
        menu2.Append(201, _('&Connect'), _('Connect the device.'))
        menu2.Append(202, _('&Disconnect'), _('Disconnect the device.'))
        menu2.AppendSeparator()
        menu2.Append(210, _('&Synchronise time'), _('Synchronise time in phone with PC.'))
        menu2.AppendSeparator()
        menu2.Append(250, _('Send &file'), _('Send file to phone.'))
        # Add menu to the menu bar
        self.menuBar.Append(menu2, _('&Phone'))

        menu3 = wx.Menu()
        menu3.Append(301, '%s\tCtrl+I' % _('&Info'), _('Retrieve phone information.'))
        menu3.AppendSeparator()
        menu3.Append(310, _('Contacts (&SIM)'), _('Retrieve contacts from SIM.'))
        menu3.Append(311, _('Contacts (&phone)'), _('Retrieve contacts from phone memory.'))
        menu3.Append(312, _('&Contacts (All)'), _('Retrieve contacts from phone and SIM memory.'))
        menu3.AppendSeparator()
        menu3.Append(320, _('C&alls'), _('Retrieve call history.'))
        menu3.AppendSeparator()
        menu3.Append(330, _('&Messages'), _('Retrieve messages.'))
        menu3.AppendSeparator()
        menu3.Append(340, _('&Todos'), _('Retrieve todos.'))
        menu3.AppendSeparator()
        menu3.Append(350, _('Calenda&r'), _('Retrieve calendar events.'))
        menu3.AppendSeparator()
        menu3.Append(399, _('A&ll'), _('Retrieve everything above.'))
        # Add menu to the menu bar
        self.menuBar.Append(menu3, _('&Retrieve'))

        menu4 = wx.Menu()
        menu4.Append(401, '%s\tCtrl+N' % _('&Contact'), _('Create new contact.'))
        menu4.Append(402, '%s\tCtrl+E' % _('Calendar &event'), _('Create new calendar event.'))
        menu4.Append(403, '%s\tCtrl+T' % _('&Todo'), _('Create new todo.'))
        menu4.Append(404, '%s\tCtrl+M' % _('&Message'), _('Create new message.'))
        # Add menu to the menu bar
        self.menuBar.Append(menu4, _('&Create'))

        menu5 = wx.Menu()
        menu5.Append(501, _('&Save'), _('Save currently retrieved data (except messages) to backup.'))
        menu5.Append(502, _('S&ave messages'), _('Save currently retrieved messages to backup.'))
        menu5.Append(503, _('&Import to phone'), _('Import data from backup to phone.'))
        menu5.Append(504, _('I&mport messages to phone'), _('Import messages from backup to phone.'))
        menu5.AppendSeparator()
        menu5.Append(510, _('Export messages to &emails'), _('Export messages to emails in storage you choose.'))
        menu5.Append(511, _('Export messages to &XML'), _('Export messages to XML file you choose.'))
        menu5.Append(512, _('Export &contacts to XML'), _('Export contacts to XML file you choose.'))
        # Add menu to the menu bar
        self.menuBar.Append(menu5, _('&Backups'))

        menuhelp = wx.Menu()
        menuhelp.Append(1001, _('&Website'), _('Visit Wammu website.'))
        menuhelp.Append(1002, _('&Support'), _('Visit Wammu support website.'))
        menuhelp.Append(1003, _('&Report bug'), _('Report bug in Wammu, please include saved debug log if possible.'))
        menuhelp.Append(1004, _('&Save debug log'), _('Save a copy of debug log, please include this in bug report.'))
        menuhelp.AppendSeparator()
        menuhelp.Append(1010, _('&Gammu Phone Database'), _('Visit database of user experiences with phones.'))
        menuhelp.Append(1011, _('&Talkback'), _('Report your experiences into Gammu Phone Database.'))
        menuhelp.AppendSeparator()
        menuhelp.Append(1020, _('&Donate'), _('Donate to Wammu project.'))
        menuhelp.AppendSeparator()
        menuhelp.Append(1100, _('&About'), _('Information about program.'))
        # Add menu to the menu bar
        self.menuBar.Append(menuhelp, _('&Help'))

        # Set menu bar
        self.SetMenuBar(self.menuBar)

        # menu events
        wx.EVT_MENU(self, 100, self.WriteData)
        wx.EVT_MENU(self, 101, self.WriteSMSData)
        wx.EVT_MENU(self, 102, self.ReadData)
        wx.EVT_MENU(self, 103, self.ReadSMSData)
        wx.EVT_MENU(self, 150, self.SearchPhone)
        wx.EVT_MENU(self, 151, self.Settings)
        wx.EVT_MENU(self, 199, self.CloseWindow)

        wx.EVT_MENU(self, 201, self.PhoneConnect)
        wx.EVT_MENU(self, 202, self.PhoneDisconnect)
        wx.EVT_MENU(self, 210, self.SyncTime)
        wx.EVT_MENU(self, 250, self.SendFile)

        wx.EVT_MENU(self, 301, self.ShowInfo)
        wx.EVT_MENU(self, 310, self.ShowContactsSM)
        wx.EVT_MENU(self, 311, self.ShowContactsME)
        wx.EVT_MENU(self, 312, self.ShowContacts)
        wx.EVT_MENU(self, 320, self.ShowCalls)
        wx.EVT_MENU(self, 330, self.ShowMessages)
        wx.EVT_MENU(self, 340, self.ShowTodos)
        wx.EVT_MENU(self, 350, self.ShowCalendar)
        wx.EVT_MENU(self, 399, self.GetAll)

        wx.EVT_MENU(self, 401, self.NewContact)
        wx.EVT_MENU(self, 402, self.NewCalendar)
        wx.EVT_MENU(self, 403, self.NewTodo)
        wx.EVT_MENU(self, 404, self.NewMessage)

        wx.EVT_MENU(self, 501, self.Backup)
        wx.EVT_MENU(self, 502, self.BackupSMS)
        wx.EVT_MENU(self, 503, self.Import)
        wx.EVT_MENU(self, 504, self.ImportSMS)
        wx.EVT_MENU(self, 510, self.SMSToMails)
        wx.EVT_MENU(self, 511, self.SMSToXML)
        wx.EVT_MENU(self, 512, self.ContactsToXML)


        wx.EVT_MENU(self, 1001, self.Website)
        wx.EVT_MENU(self, 1002, self.Support)
        wx.EVT_MENU(self, 1003, self.ReportBug)
        wx.EVT_MENU(self, 1004, self.SaveLog)
        wx.EVT_MENU(self, 1010, self.PhoneDB)
        wx.EVT_MENU(self, 1011, self.Talkback)
        wx.EVT_MENU(self, 1020, self.Donate)
        wx.EVT_MENU(self, 1100, self.About)

        self.timer = None
        self.TogglePhoneMenus(False)

        self.type = ['info', '  ']

        self.TimerId = wx.NewId()

        if Wammu.gammu_error is None:
            # create state machine
            self.sm = gammu.StateMachine()

            # create temporary file for logs
            fd, self.logfilename = tempfile.mkstemp('.log', 'wammu')

            # set filename to be used for error reports
            Wammu.ErrorLog.DEBUG_LOG_FILENAME = self.logfilename

            if sys.platform != 'win32':
                print ConsoleStrConv(
                    _('Debug log created in temporary file <%s>. In case of crash please include it in bugreport!') % self.logfilename
                    )

            self.logfilefd = os.fdopen(fd, 'w+')
            # use temporary file for logs
            gammu.SetDebugFile(self.logfilefd)
            gammu.SetDebugLevel('textalldate')

            if Wammu.debug:
                self.loggerdebug = Wammu.Logger.LoggerDebug(self.logfilename)
                self.loggerdebug.start()

        # initialize variables
        self.showdebug = ''
        self.IMEI = ''
        self.Manufacturer = ''
        self.Model = ''
        self.Version = ''
        self.tbicon = None

    def OutdatedData(self):
        wx.MessageDialog(
            self,
            _('You can not work on this data, please retrieve it first from phone'),
            _('Data not up to date'),
            wx.OK | wx.ICON_ERROR
        ).ShowModal()

    def HandleGammuError(self):
        '''
        Show error about gammu import failure. Try to help user with various
        situation which could happened, so that he can solve this problem.
        '''
        error = str(Wammu.gammu_error)
        if error.find('Runtime libGammu version does not match compile time version') != -1:
            result = re.match('Runtime libGammu version does not match compile time version \(runtime: (\S+), compiletime: (\S+)\)', error)

            wx.MessageDialog(
                self,
                _('Wammu could not import gammu module, program will be terminated.') + '\n\n' +
                _('The import failed because python-gammu is compiled with different version of Gammu than it is now using (it was compiled with version %(compile)s and now it is using version %(runtime)s).') % {'compile': result.group(2), 'runtime': result.group(1)} + '\n\n' +
                _('You can fix it by recompiling python-gammu against gammu library you are currently using.'),
                _('Gammu module not working!'),
                wx.OK | wx.ICON_ERROR).ShowModal()
        elif error.find('No module named gammu') != -1:
            wx.MessageDialog(
                self,
                _('Wammu could not import gammu module, program will be terminated.') + '\n\n' +
                _('Gammu module was not found, you probably don\'t have properly installed python-gammu for current python version.'),
                _('Gammu module not working!'),
                wx.OK | wx.ICON_ERROR
            ).ShowModal()
        else:
            wx.MessageDialog(
                self,
                _('Wammu could not import gammu module, program will be terminated.') + '\n\n' +
                _('The import failed with following error:') + '\n\n%s' % error,
                _('Gammu module not working!'),
                wx.OK | wx.ICON_ERROR
            ).ShowModal()
        sys.exit()

    def InitConfiguration(self):
        '''
        Binds Wammu configuration to Gammu one. If at least one section
        exists, use first one (same as Gammu), otherwise we suggest search to
        user.
        '''
        gammucfg = self.cfg.gammu.GetConfigs()
        if len(gammucfg) == 0:
            dlg = wx.MessageDialog(
                self,
                _('Wammu configuration was not found and Gammu settings couldn\'t be read.') + '\n\n' +
                _('Do you want to configure phone connection now?') + '\n',
                _('Configuration not found'),
                wx.YES_NO | wx.YES_DEFAULT | wx.ICON_WARNING
            )
            if dlg.ShowModal() == wx.ID_YES:
                self.SearchPhone()
        elif not self.cfg.HasEntry('/Gammu/Section'):
            # behave as Gammu
            self.cfg.WriteInt('/Gammu/Section', 0)

    def TalkbackCheck(self):
        '''
        Do ask for talkback after month of usage and at least 30 executions.
        '''
        firstrun = self.cfg.ReadFloat('/Wammu/FirstRun')
        if firstrun == -1:
            firstrun = time.time()
            self.cfg.WriteFloat('/Wammu/FirstRun', firstrun)
        runs = self.cfg.ReadInt('/Wammu/RunCounter')
        self.cfg.WriteInt('/Wammu/RunCounter', runs + 1)
        if self.cfg.Read('/Wammu/TalkbackDone') == 'no':
            if (firstrun + (3600 * 24 * TALKBACK_DAYS) < time.time()
                    and runs > TALKBACK_COUNT):
                dlg = wx.MessageDialog(
                    self,
                    _('You are using Wammu for more than a month. We would like to hear from you how your phone is supported. Do you want to participate in this survey?') +
                    '\n\n' + _('Press Cancel to never show this question again.'),
                    _('Thanks for using Wammu'),
                    wx.YES_NO | wx.CANCEL | wx.ICON_INFORMATION
                )
                ret = dlg.ShowModal()
                if ret == wx.ID_YES:
                    self.Talkback()
                elif ret == wx.ID_CANCEL:
                    self.cfg.Write('/Wammu/TalkbackDone', 'skipped')

    def MigrateConfiguration(self):
        '''
        Migrate configuration from pre-0.18 style one (Gammu was configured
        inside Wammu configuration) to using .gammurc.
        '''
        connection = self.cfg.Read('/Gammu/Connection')
        device = self.cfg.Read('/Gammu/Device')
        model = self.cfg.Read('/Gammu/Model')
        gammucfg = self.cfg.gammu.GetConfigs()
        if len(gammucfg) > 0:
            for i in gammucfg:
                cfg = self.cfg.gammu.GetConfig(i['Id'])
                if cfg['Model'] == model and cfg['Connection'] == connection and cfg['Device'] == device:
                    self.cfg.WriteInt('/Gammu/Section', i['Id'])
                    break
            if not self.cfg.HasEntry('/Gammu/Section'):
                index = self.cfg.gammu.FirstFree()
                self.cfg.gammu.SetConfig(index, device, connection, _('Migrated from older Wammu'), model)
                self.cfg.WriteInt('/Gammu/Section', index)

    def PostInit(self, appparent):
        '''
        Do things which need window opened to behave correctly.

        - Activate initial view.
        - Show if something wrong has happened on gammu import.
        - Initialize or migrate Gammu configuration.
        - Connect to phone if required.
        - Ask for talkback.
        - Setup internal information.
        '''
        self.ActivateView('info', '  ')
        self.appparent = appparent

        if Wammu.gammu_error is not None:
            self.HandleGammuError()

        if not self.cfg.HasEntry('/Gammu/Section') and self.cfg.HasEntry('/Gammu/Connection'):
            self.MigrateConfiguration()

        self.InitConfiguration()

        self.DoDebug(self.cfg.Read('/Debug/Show'))

        if self.cfg.Read('/Wammu/AutoConnect') == 'yes':
            self.PhoneConnect()

        self.TalkbackCheck()

        self.SetupNumberPrefix()

        self.SetupStatusRefresh()

        self.SetupTrayIcon()

        self.InitDBUS()

    def InitDBUS(self):
        '''
        Initializes DBUS handlers if available.
        '''
        self.dbus_notify = None
        self.last_dbus_id = 0
        if HAVE_DBUS:
            try:
                bus = dbus.SessionBus() # mainloop=self.appparent.MainLoop)
                interface = 'org.freedesktop.Notifications'
                path = '/org/freedesktop/Notifications'
                if Wammu.Utils.DBUSServiceAvailable(bus, interface, True):
                    obj = bus.get_object(interface, path)
                    self.dbus_notify = dbus.Interface(obj, interface)
                    self.dbus_notify.connect_to_signal('ActionInvoked', self.DBUSActionCallback)
            except dbus.DBusException:
                self.dbus_notify = None
                self.last_dbus_id = 0

    def SetupTrayIcon(self):
        if self.cfg.Read('/Wammu/TaskBarIcon') != 'yes':
            if self.tbicon is not None:
                self.tbicon.Destroy()
                self.tbicon = None
            return
        if self.tbicon is not None:
            # Nothing to do
            return
        self.tbicon = wx.TaskBarIcon()
        self.tbicon.SetIcon(self.icon16, 'Wammu')
        self.tbicon.Bind(wx.EVT_TASKBAR_RIGHT_UP, self.OnTaskBarRightClick)
        self.tbicon.Bind(wx.EVT_TASKBAR_LEFT_UP, self.OnTaskBarLeftClick)
        self.tbicon.Bind(wx.EVT_MENU, self.Settings, id=151)
        self.tbicon.Bind(wx.EVT_MENU, self.PhoneConnect, id=201)
        self.tbicon.Bind(wx.EVT_MENU, self.PhoneDisconnect, id=202)
        self.tbicon.Bind(wx.EVT_MENU, self.OnTaskBarRestore, id=100000)
        self.tbicon.Bind(wx.EVT_MENU, self.OnTaskBarMinimize, id=100001)
        self.tbicon.Bind(wx.EVT_MENU, self.OnTaskBarClose, id=100002)

    def OnTaskBarRightClick(self, evt):
        menutaskbar = wx.Menu()
        menutaskbar.Append(201, _('Connect'))
        menutaskbar.Append(202, _('Disconnect'))
        menutaskbar.AppendSeparator()
        menutaskbar.Append(151, _('Settings'))
        menutaskbar.AppendSeparator()
        menutaskbar.Append(100000, _('Restore'))
        menutaskbar.Append(100001, _('Minimize'))
        menutaskbar.AppendSeparator()
        menutaskbar.Append(100002, _('Close'))
        self.tbicon.PopupMenu(menutaskbar)
        menutaskbar.Destroy()

    def OnTaskBarLeftClick(self, evt):
        if self.IsShown():
            self.Show(False)
        else:
            self.Show(True)

    def OnTaskBarRestore(self, evt):
        self.Show(True)

    def OnTaskBarMinimize(self, evt):
        self.Show(False)

    def OnTaskBarClose(self, evt):
        self.CloseWindow(evt)

    def OnTimer(self, evt=None):
        if self.connected:
            try:
                s = self.sm.GetSignalQuality()
                b = self.sm.GetBatteryCharge()
                d = self.sm.GetDateTime()

                # Parse power source
                power = _('Unknown')
                if b['ChargeState'] == 'BatteryPowered':
                    power = _('battery')
                elif b['ChargeState'] == 'BatteryConnected':
                    power = _('AC')
                elif b['ChargeState'] == 'BatteryNotConnected':
                    power = _('no battery')
                elif b['ChargeState'] == 'PowerFault':
                    power = _('fault')
                elif b['ChargeState'] == 'BatteryCharging':
                    power = _('charging')
                elif b['ChargeState'] == 'BatteryFull':
                    power = _('charged')

                # Time might be None if it is invalid (eg. 0.0.0000 date)
                if d is None:
                    time = _('Unknown')
                else:
                    time = StrConv(d.strftime('%c'))

                # Detect unknown signal quality
                if s['SignalPercent'] == -1:
                    signal = _('Unknown')
                else:
                    # l10n: Formatting of signal percentage, usually you can keep this as it is.
                    signal = _('%d %%') % s['SignalPercent']

                self.SetStatusText(_('Bat: %(battery_percent)d %% (%(power_source)s), Sig: %(signal_level)s, Time: %(time)s') % {
                        'battery_percent': b['BatteryPercent'],
                        'power_source': power,
                        'signal_level': signal,
                        'time': time
                    }, 1)
            except gammu.GSMError:
                pass

    def SetupNumberPrefix(self):
        self.prefix = self.cfg.Read('/Wammu/PhonePrefix')
        if self.prefix == 'Auto':
            if self.connected:
                self.prefix = None
                try:
                    on = Wammu.Utils.ParseMemoryEntry(self.sm.GetMemory(Location=1, Type='ON'), self.cfg)['Number']
                    self.prefix = Wammu.Utils.GrabNumberPrefix(on, Wammu.Data.InternationalPrefixes)
                except gammu.GSMError:
                    pass
                if self.prefix is None:
                    try:
                        smsc = self.sm.GetSMSC()['Number']
                        self.prefix = Wammu.Utils.GrabNumberPrefix(smsc, Wammu.Data.InternationalPrefixes)
                    except gammu.GSMError:
                        pass
                if self.prefix is None:
                    self.prefix = self.cfg.Read('/Wammu/LastPhonePrefix')
                else:
                    self.cfg.Write('/Wammu/LastPhonePrefix', self.prefix)
            else:
                self.prefix = self.cfg.Read('/Wammu/LastPhonePrefix')
        Wammu.Utils.NumberPrefix = self.prefix

    def SetupStatusRefresh(self):
        repeat = self.cfg.ReadInt('/Wammu/RefreshState')
        if repeat == 0:
            self.timer = None
        else:
            self.OnTimer()
            self.timer = wx.Timer(self, self.TimerId)
            wx.EVT_TIMER(self, self.TimerId, self.OnTimer)
            self.timer.Start(repeat)

    def DoDebug(self, newdebug):
        if newdebug != self.showdebug:
            self.showdebug = newdebug
            if self.showdebug == 'yes':
                self.logwin = Wammu.Logger.LogFrame(self, self.cfg)
                self.logwin.Show(True)
                wx.EVT_CLOSE(self.logwin, self.LogClose)
                self.logger = Wammu.Logger.Logger(self.logwin, self.logfilename)
                self.logger.start()
            else:
                self.CloseLogWindow()

    def SaveWinSize(self, win, key):
        x, y = win.GetPositionTuple()
        w, h = win.GetSizeTuple()

        self.cfg.WriteInt('/%s/X' % key, x)
        self.cfg.WriteInt('/%s/Y' % key, y)
        self.cfg.WriteInt('/%s/Width' % key, w)
        self.cfg.WriteInt('/%s/Height' % key, h)

    def CloseLogWindow(self):
        if hasattr(self, 'logwin'):
            self.SaveWinSize(self.logwin, 'Debug')
        if hasattr(self, 'logger'):
            self.logger.canceled = True
            del self.logger
        if hasattr(self, 'logwin'):
            self.logwin.Destroy()
            del self.logwin


    def LogClose(self, evt=None):
        self.cfg.Write('/Debug/Show', 'no')
        self.CloseLogWindow()

    def TogglePhoneMenus(self, enable):
        self.connected = enable
        if enable:
            self.SetStatusText(_('Connected'), 1)
            if self.timer is not None:
                self.OnTimer()
        else:
            self.SetStatusText(_('Disconnected'), 1)
        mb = self.menuBar

        mb.Enable(201, not enable)
        mb.Enable(202, enable)

        mb.Enable(210, enable)

        mb.Enable(250, enable)

        mb.Enable(301, enable)

        mb.Enable(310, enable)
        mb.Enable(311, enable)
        mb.Enable(312, enable)

        mb.Enable(320, enable)

        mb.Enable(330, enable)

        mb.Enable(340, enable)

        mb.Enable(350, enable)

        mb.Enable(399, enable)

        mb.Enable(401, enable)
        mb.Enable(402, enable)
        mb.Enable(403, enable)
        mb.Enable(404, enable)

        mb.Enable(501, enable)
        mb.Enable(502, enable)
        mb.Enable(503, enable)
        mb.Enable(504, enable)

        mb.Enable(510, enable)
        mb.Enable(511, enable)
        mb.Enable(512, enable)

    def ActivateView(self, k1, k2):
        self.tree.SelectItem(self.treei[k1][k2])
        self.ChangeView(k1, k2)

    def ChangeView(self, k1, k2):
        self.ChangeBrowser(k1, k2)
        self.righttitle.SetLabel(displaydata[k1][k2][2])

    def ChangeBrowser(self, k1, k2):
        self.type = [k1, k2]
        if k2 == '  ':
            data = []
            for k3, v3 in self.values[k1].iteritems():
                if k3 != '__':
                    data = data + v3
            self.values[k1]['__'] = data
            self.browser.Change(k1, data)
        else:
            self.browser.Change(k1, self.values[k1][k2])
        self.browser.ShowRow(0)

    def OnTreeSel(self, event):
        item = event.GetItem()
        for k1, v1 in self.treei.iteritems():
            for k2, v2 in v1.iteritems():
                if v2 == item:
                    self.ChangeView(k1, k2)
        self.ClearSearch()

    def OnSearch(self, event):
        text = self.searchinput.GetValue()
        type = self.searchchoice.GetSelection()
        try:
            self.browser.Filter(text, type)
            self.searchinput.SetBackgroundColour(wx.NullColour)
        except Wammu.Browser.FilterException:
            self.searchinput.SetBackgroundColour(wx.RED)

    def ClearSearch(self, event=None):
        self.searchinput.SetValue('')

    def Settings(self, event=None):
        if self.connected:
            connection_settings = {
                'Connection': self.cfg.Read('/Gammu/Connection'),
                'LockDevice': self.cfg.ReadBool('/Gammu/LockDevice'),
                'Device': self.cfg.Read('/Gammu/Device'),
                'Model': self.cfg.Read('/Gammu/Model')
            }

        result = Wammu.Settings.Settings(self, self.cfg).ShowModal()
        if result == wx.ID_OK:
            if self.connected:
                connection_settings_new = {
                    'Connection': self.cfg.Read('/Gammu/Connection'),
                    'LockDevice': self.cfg.ReadBool('/Gammu/LockDevice'),
                    'Device': self.cfg.Read('/Gammu/Device'),
                    'Model': self.cfg.Read('/Gammu/Model')
                }

                if connection_settings != connection_settings_new:
                    wx.MessageDialog(
                        self,
                        _('You changed parameters affecting phone connection, they will be used next time you connect to phone.'),
                        _('Notice'),
                        wx.OK | wx.ICON_INFORMATION
                    ).ShowModal()
            self.DoDebug(self.cfg.Read('/Debug/Show'))
            self.SetupNumberPrefix()
            self.SetupStatusRefresh()
            self.SetupTrayIcon()

    def CloseWindow(self, event):
        self.SaveWinSize(self, 'Main')
        if hasattr(self, 'logwin'):
            self.CloseLogWindow()
        self.cfg.WriteInt('/Main/Split', self.splitter.GetSashPosition())
        self.cfg.WriteInt('/Main/SplitRight', self.rightsplitter.GetSashPosition())
        self.cfg.WriteInt('/Defaults/SearchType', self.searchchoice.GetCurrentSelection())

        gammu.SetDebugFile(None)
        gammu.SetDebugLevel('nothing')

        self.logfilefd.close()

        if hasattr(self, 'logger'):
            self.logger.canceled = True
            self.logger.join()

        if hasattr(self, 'loggerdebug'):
            self.loggerdebug.canceled = True
            self.loggerdebug.join()

        if self.tbicon is not None:
            self.tbicon.Destroy()

        if sys.platform != 'win32':
            print ConsoleStrConv(
                _('Looks like normal program termination, deleting log file.')
                )
        try:
            os.unlink(self.logfilename)
        except:
            print ConsoleStrConv(
                _('Failed to unlink temporary log file, please delete it yourself.')
                )
            print ConsoleStrConv(
                _('Filename: %s') % self.logfilename
                )

        # Forcibily save configuration
        self.cfg.Flush()

        # tell the window to kill itself
        self.Destroy()

    def ShowError(self, info):
        try:
            gammu_config = self.gammu_config
        except AttributeError:
            gammu_config = None
        evt = Wammu.Events.ShowMessageEvent(
            message=Wammu.Utils.FormatError(_('Error while communicating with phone'), info, gammu_config=gammu_config),
            title=_('Error Occured'),
            errortype='gammu',
            type=wx.ICON_ERROR
        )
        wx.PostEvent(self, evt)

    def ShowProgress(self, text):
        self.progress = wx.ProgressDialog(
                        _('Operation in progress'),
                        text,
                        100,
                        self,
                        wx.PD_CAN_ABORT | wx.PD_APP_MODAL | wx.PD_AUTO_HIDE | wx.PD_ELAPSED_TIME | wx.PD_REMAINING_TIME | wx.PD_ESTIMATED_TIME)

    def OnProgress(self, evt):
        if hasattr(self, 'progress'):
            if not self.progress.Update(evt.progress):
                try:
                    evt.cancel()
                except:
                    pass
            if evt.progress == 100 and hasattr(self, 'progress'):
                del self.progress
        if hasattr(evt, 'lock'):
            evt.lock.release()

    def OnException(self, evt):
        Wammu.Error.Handler(*evt.data)

    def OnData(self, evt):
        self.values[evt.type[0]][evt.type[1]] = evt.data
        if evt.last:
            if hasattr(self, 'progress'):
                self.progress.Update(100)
                del self.progress

            if hasattr(self, 'nextfun'):
                f = self.nextfun
                a = self.nextarg
                del self.nextfun
                del self.nextarg
                f (*a)

    def ShowData(self, data):
        text = u''
        if data is not None:
            for d in data:
                if len(d) == 2:
                    text += u'<b>%s</b>: %s<br>' % (d[0], d[1])
                else:
                    text += u'<p>%s</p>' % d[0]
        self.content.SetContent(text)

    def OnShow(self, evt):
        data = v = evt.data
        if data is None:
            pass
        elif self.type == ['info', '  ']:
            data = [(evt.data['Name'], evt.data['Value'])]
        elif self.type[0] == 'contact' or self.type[0] == 'call':
            data = [
                (_('Location'), str(v['Location'])),
                (_('Memory type'), v['MemoryType'])]
            for i in v['Entries']:
                s = Wammu.Utils.GetTypeString(i['Type'], i['Value'], self.values, linkphone=False)
                try:
                    if i['VoiceTag']:
                        s += ', ' + (_('voice tag %x') % i['VoiceTag'])
                except:
                    pass
                data.append((i['Type'], s))
        elif self.type[0] == 'message':
            data = [
                (_('Number'), Wammu.Utils.GetNumberLink([] + self.values['contact']['ME'] + self.values['contact']['SM'], v['Number'])),
                (_('Date'), StrConv(v['DateTime'])),
                (_('Location'), StrConv(v['Location'])),
                (_('Folder'), StrConv(v['SMS'][0]['Folder'])),
                (_('Memory'), StrConv(v['SMS'][0]['Memory'])),
                (_('SMSC'), Wammu.Utils.GetNumberLink([] + self.values['contact']['ME'] + self.values['contact']['SM'], v['SMS'][0]['SMSC']['Number'])),
                (_('Status'), StrConv(v['State']))]
            if v['Name'] != '':
                data.append((_('Name'), StrConv(v['Name'])))
            data.append((Wammu.MessageDisplay.SmsToHtml(self.cfg, v),))
        elif self.type[0] == 'todo':
            data = [
                (_('Location'), str(v['Location'])),
                (_('Priority'), v['Priority']),
                (_('Type'), v['Type']),
                ]
            for i in v['Entries']:
                data.append((i['Type'], Wammu.Utils.GetTypeString(i['Type'], i['Value'], self.values)))
        elif self.type[0] == 'calendar':
            data = [
                (_('Location'), str(v['Location'])),
                (_('Type'), v['Type']),
                ]
            for i in v['Entries']:
                data.append((i['Type'], Wammu.Utils.GetTypeString(i['Type'], i['Value'], self.values)))
        else:
            data = [('Show not yet implemented! (type=%s)' % self.type[0])]
        self.ShowData(data)

    def NewContact(self, evt):
        self.EditContact({})

    def NewCalendar(self, evt):
        self.EditCalendar({})

    def NewTodo(self, evt):
        self.EditTodo({})

    def NewMessage(self, evt):
        self.ComposeMessage({})

    def ComposeMessage(self, v, action='save'):
        if Wammu.Composer.SMSComposer(self, self.cfg, v, self.values, action).ShowModal() == wx.ID_OK:

            if len(v['Numbers']) == 0:
                v['Numbers'] = ['Wammu']

            for number in v['Numbers']:
                busy = wx.BusyInfo(_('Writing message(s)...'))
                time.sleep(0.1)
                wx.Yield()
                v['Number'] = number
                v['SMS'] = gammu.EncodeSMS(v['SMSInfo'])

                if v['Save']:
                    result = {}
                    result['SMS'] = []

                try:
                    for msg in v['SMS']:
                        msg['SMSC']['Location'] = 1

                        msg['Folder'] = v['Folder']
                        msg['Number'] = v['Number']
                        msg['Type'] = v['Type']
                        msg['State'] = v['State']

                        if v['Save']:
                            msg['Location'], msg['Folder'] = self.sm.AddSMS(msg)
                            if v['Send']:
                                # When sending of saved message fails, send it directly:
                                try:
                                    msg['MessageReference'] = self.sm.SendSavedSMS(0, msg['Location'])
                                except gammu.GSMError:
                                    msg['MessageReference'] = self.sm.SendSMS(msg)
                            try:
                                result['SMS'].append(self.sm.GetSMS(0, msg['Location'])[0])
                            except gammu.ERR_EMPTY:
                                wx.MessageDialog(
                                    self,
                                    _('It was not possible to read saved message! There is most likely some bug in Gammu, please contact author with debug log of this operation. To see message in Wammu you need to reread all messsages.'),
                                    _('Could not read saved message!'),
                                    wx.OK | wx.ICON_ERROR
                                ).ShowModal()
                        elif v['Send']:
                            msg['MessageReference'] = self.sm.SendSMS(msg)

                    if v['Save']:
                        info = gammu.DecodeSMS(result['SMS'])
                        if info is not None:
                            result['SMSInfo'] = info
                        Wammu.Utils.ParseMessage(result, (info is not None))
                        result['Synced'] = True
                        self.values['message'][result['State']].append(result)

                except gammu.GSMError as val:
                    del busy
                    self.ShowError(val.args[0])
                except:
                    del busy
                    raise

            if v['Save']:
                try:
                    self.ActivateView('message', result['State'])
                    self.browser.ShowLocation(result['Location'])
                except KeyError:
                    pass

    def EditContact(self, v):
        backup = copy.deepcopy(v)
        shoulddelete = (v == {} or v['Location'] == 0)
        if Wammu.Editor.ContactEditor(self, self.cfg, self.values, v).ShowModal() == wx.ID_OK:
            try:
                busy = wx.BusyInfo(_('Writing contact...'))
                time.sleep(0.1)
                wx.Yield()
                # was entry moved => delete it from internal list
                if not shoulddelete:
                    for idx in range(len(self.values['contact'][backup['MemoryType']])):
                        if self.values['contact'][backup['MemoryType']][idx] == v:
                            del self.values['contact'][backup['MemoryType']][idx]
                            break

                # have we specified location? => add or set
                if v['Location'] == 0:
                    v['Location'] = self.sm.AddMemory(v)
                else:
                    try:
                        v['Location'] = self.sm.SetMemory(v)
                    except (gammu.ERR_NOTSUPPORTED, gammu.ERR_NOTIMPLEMENTED):
                        v['Location'] = self.sm.AddMemory(v)

                # was entry moved => delete it from phone
                if not shoulddelete:
                    if v['MemoryType'] != backup['MemoryType'] or  v['Location'] != backup['Location']:
                        # delete from phone
                        self.sm.DeleteMemory(backup['MemoryType'], backup['Location'])

                # reread entry (it doesn't have to contain exactly same data as entered, it depends on phone features)
                try:
                    attempts = 0
                    while attempts < 10:
                        try:
                            v = self.sm.GetMemory(v['MemoryType'], v['Location'])
                            break
                        except gammu.ERR_EMPTY:
                            # some phones need time till entry appears
                            attempts = attempts + 1
                            time.sleep(0.2)
                except (gammu.ERR_NOTSUPPORTED, gammu.ERR_NOTIMPLEMENTED):
                    wx.MessageDialog(
                        self,
                        _('It was not possible to read saved entry! It might be different than one saved in phone untill you reread all entries.'),
                        _('Could not read saved entry!'),
                        wx.OK | wx.ICON_WARNING
                    ).ShowModal()
                Wammu.Utils.ParseMemoryEntry(v, self.cfg)
                v['Synced'] = True
                # append new value to list
                self.values['contact'][v['MemoryType']].append(v)

            except gammu.GSMError as val:
                del busy
                v = backup
                self.ShowError(val.args[0])
            except:
                del busy
                raise

            if (self.type[0] == 'contact' and self.type[1] == '  ') or 'MemoryType' not in v:
                self.ActivateView('contact', '  ')
                try:
                    self.browser.ShowLocation(v['Location'], ('MemoryType', v['MemoryType']))
                except KeyError:
                    pass
            else:
                self.ActivateView('contact', v['MemoryType'])
                try:
                    self.browser.ShowLocation(v['Location'])
                except KeyError:
                    pass

    def EditCalendar(self, v):
        backup = copy.deepcopy(v)
        shoulddelete = (v == {} or v['Location'] == 0)
        if Wammu.Editor.CalendarEditor(self, self.cfg, self.values, v).ShowModal() == wx.ID_OK:
            try:
                busy = wx.BusyInfo(_('Writing calendar...'))
                time.sleep(0.1)
                wx.Yield()
                # was entry moved => delete it from internal list
                if not shoulddelete:
                    # delete from internal list
                    for idx in range(len(self.values['calendar']['  '])):
                        if self.values['calendar']['  '][idx] == v:
                            del self.values['calendar']['  '][idx]
                            break

                # have we specified location? => add or set
                if v['Location'] == 0:
                    v['Location'] = self.sm.AddCalendar(v)
                else:
                    try:
                        v['Location'] = self.sm.SetCalendar(v)
                    except (gammu.ERR_NOTSUPPORTED, gammu.ERR_NOTIMPLEMENTED):
                        v['Location'] = self.sm.AddCalendar(v)

                # was entry moved => delete it from phone
                if not shoulddelete:
                    if v['Location'] != backup['Location']:
                        # delete from phone
                        self.sm.DeleteCalendar(backup['Location'])

                # reread entry (it doesn't have to contain exactly same data as entered, it depends on phone features)
                try:
                    v = self.sm.GetCalendar(v['Location'])
                except (gammu.ERR_NOTSUPPORTED, gammu.ERR_NOTIMPLEMENTED):
                    wx.MessageDialog(
                        self,
                        _('It was not possible to read saved entry! It might be different than one saved in phone untill you reread all entries.'),
                        _('Could not read saved entry!'),
                        wx.OK | wx.ICON_WARNING
                    ).ShowModal()
                Wammu.Utils.ParseCalendar(v)
                v['Synced'] = True
                # append new value to list
                self.values['calendar']['  '].append(v)

            except gammu.GSMError as val:
                del busy
                v = backup
                self.ShowError(val.args[0])
            except:
                del busy
                raise

            self.ActivateView('calendar', '  ')
            try:
                self.browser.ShowLocation(v['Location'])
            except KeyError:
                pass

    def EditTodo(self, v):
        backup = copy.deepcopy(v)
        shoulddelete = (v == {} or v['Location'] == 0)
        if Wammu.Editor.TodoEditor(self, self.cfg, self.values, v).ShowModal() == wx.ID_OK:
            try:
                busy = wx.BusyInfo(_('Writing todo...'))
                time.sleep(0.1)
                wx.Yield()
                # was entry moved => delete it from internal list
                if not shoulddelete:
                    for idx in range(len(self.values['todo']['  '])):
                        if self.values['todo']['  '][idx] == v:
                            del self.values['todo']['  '][idx]
                            break

                # have we specified location? => add or set
                if v['Location'] == 0:
                    v['Location'] = self.sm.AddToDo(v)
                else:
                    try:
                        v['Location'] = self.sm.SetToDo(v)
                    except (gammu.ERR_NOTSUPPORTED, gammu.ERR_NOTIMPLEMENTED):
                        v['Location'] = self.sm.AddToDo(v)

                # was entry moved => delete it from phone
                if not shoulddelete:
                    if v['Location'] != backup['Location']:
                        # delete from phone
                        self.sm.DeleteToDo(backup['Location'])

                # reread entry (it doesn't have to contain exactly same data as entered, it depends on phone features)
                try:
                    v = self.sm.GetToDo(v['Location'])
                except (gammu.ERR_NOTSUPPORTED, gammu.ERR_NOTIMPLEMENTED):
                    wx.MessageDialog(self, _('It was not possible to read saved entry! It might be different than one saved in phone untill you reread all entries.'), _('Could not read saved entry!'), wx.OK | wx.ICON_WARNING).ShowModal()
                Wammu.Utils.ParseTodo(v)
                v['Synced'] = True
                # append new value to list
                self.values['todo']['  '].append(v)
            except gammu.GSMError as val:
                del busy
                v = backup
                self.ShowError(val.args[0])
            except:
                del busy
                raise

            self.ActivateView('todo', '  ')
            try:
                self.browser.ShowLocation(v['Location'])
            except KeyError:
                pass


    def OnEdit(self, evt):
        if evt.data != {} and not evt.data['Synced']:
            self.OutdatedData()
            return
        if self.type[0] == 'contact':
            self.EditContact(evt.data)
        elif self.type[0] == 'call' and evt.data['Location'] == 0:
            self.EditContact(evt.data)
        elif self.type[0] == 'calendar':
            self.EditCalendar(evt.data)
        elif self.type[0] == 'todo':
            self.EditTodo(evt.data)
        else:
            print 'Edit not yet implemented (type=%s)!' % self.type[0]

    def OnReply(self, evt):
        if self.type[0] == 'message':
            self.ComposeMessage({'Number': evt.data['Number']}, action='send')
        else:
            print 'Reply not yet implemented!'
            print evt.index

    def OnCall(self, evt):
        if self.type[0] in ['call', 'contact']:
            num = Wammu.Select.SelectContactNumber(self, evt.data)
            if num is None:
                return

            try:
                self.sm.DialVoice(num)
            except gammu.GSMError as val:
                self.ShowError(val.args[0])
        elif self.type[0] == 'message':
            try:
                self.sm.DialVoice(evt.data['Number'])
            except gammu.GSMError as val:
                self.ShowError(val.args[0])
        else:
            print 'Call not yet implemented (type=%s)!' % self.type[0]

    def OnMessage(self, evt):
        if self.type[0] in ['call', 'contact']:

            num = Wammu.Select.SelectContactNumber(self, evt.data)
            if num is None:
                return
            self.ComposeMessage({'Number': num}, action='send')
        elif self.type[0] == 'message':
            self.ComposeMessage({'Number': evt.data['Number']}, action='send')
        else:
            print 'Message send not yet implemented (type=%s)!' % self.type[0]

    def OnDuplicate(self, evt):
        if evt.data != {} and not evt.data['Synced']:
            self.OutdatedData()
            return
        v = copy.deepcopy(evt.data)
        if self.type[0] == 'contact':
            v['Location'] = 0
            self.EditContact(v)
        elif self.type[0] == 'calendar':
            v['Location'] = 0
            self.EditCalendar(v)
        elif self.type[0] == 'todo':
            v['Location'] = 0
            self.EditTodo(v)
        elif self.type[0] == 'message':
            self.ComposeMessage(v)
        else:
            print 'Duplicate not yet implemented (type=%s)!' % self.type[0]


    def OnSend(self, evt):
        if evt.data != {} and not evt.data['Synced']:
            self.OutdatedData()
            return
        if self.type[0] == 'message':
            v = evt.data
            try:
                try:
                    for loc in v['Location'].split(', '):
                        self.sm.SendSavedSMS(0, int(loc))
                except gammu.ERR_NOTSUPPORTED:
                    for msg in v['SMS']:
                        self.sm.SendSMS(msg)
            except gammu.GSMError as val:
                self.ShowError(val.args[0])

    def SMSToMails(self, evt):
        messages = self.values['message']['Read'] + \
            self.values['message']['UnRead'] + \
            self.values['message']['Sent'] + \
            self.values['message']['UnSent']
        contacts = self.values['contact']['ME'] + \
            self.values['contact']['SM']
        Wammu.SMSExport.SMSExport(self, messages, contacts)

    def SMSToXML(self, evt):
        messages = self.values['message']['Read'] + \
            self.values['message']['UnRead'] + \
            self.values['message']['Sent'] + \
            self.values['message']['UnSent']
        contacts = self.values['contact']['ME'] + \
            self.values['contact']['SM']
        Wammu.SMSXML.SMSExportXML(self, messages, contacts)

    def ContactsToXML(self, evt):
        Wammu.ContactsXML.ContactsExportXML(self, self.values['contact']['SM'], self.values['contact']['ME'])

    def SelectBackupFile(self, type, save=True, data=False):
        wildcard = ''
        if type == 'message':
            wildcard += _('Gammu messages backup') + ' (*.smsbackup)|*.smsbackup|'
            exts = ['smsbackup']
        else:
            if not save:
                wildcard += _('All backup formats') + '|*.backup;*.lmb;*.vcf;*.ldif;*.vcs;*.ics|'

            wildcard += _('Gammu backup [all data]') + ' (*.backup)|*.backup|'
            exts = ['backup']

            if type in ['contact', 'all']:
                wildcard += _('Nokia backup [contacts]') + ' (*.lmb)|*.lmb|'
                exts.append('lmb')
            if type in ['contact', 'all']:
                wildcard += _('vCard [contacts]') + ' (*.vcf)|*.vcf|'
                exts.append('vcf')
            if type in ['contact', 'all']:
                wildcard += _('LDIF [contacts]') + ' (*.ldif)|*.ldif|'
                exts.append('ldif')
            if type in ['todo', 'calendar', 'all']:
                wildcard += _('vCalendar [todo,calendar]') + ' (*.vcs)|*.vcs|'
                exts.append('vcs')
            if type in ['todo', 'calendar', 'all']:
                wildcard += _('iCalendar [todo,calendar]') + ' (*.ics)|*.ics|'
                exts.append('ics')

        wildcard += _('All files') + ' (*.*)|*.*'
        exts.append(None)

        if data:
            if save:
                dlg = wx.FileDialog(
                    self,
                    _('Save data as...'),
                    os.getcwd(),
                    "",
                    wildcard,
                    wx.SAVE | wx.OVERWRITE_PROMPT | wx.CHANGE_DIR
                )
            else:
                dlg = wx.FileDialog(
                    self,
                    _('Read data'),
                    os.getcwd(),
                    "",
                    wildcard,
                    wx.OPEN | wx.CHANGE_DIR
                )
        else:
            if save:
                dlg = wx.FileDialog(
                    self,
                    _('Save backup as...'),
                    os.getcwd(),
                    "",
                    wildcard,
                    wx.SAVE | wx.OVERWRITE_PROMPT | wx.CHANGE_DIR
                )
            else:
                dlg = wx.FileDialog(
                    self,
                    _('Import backup'),
                    os.getcwd(),
                    "",
                    wildcard,
                    wx.OPEN | wx.CHANGE_DIR
                )
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            if save:
                ext = exts[dlg.GetFilterIndex()]
                # Add automatic extension if we know one and file does not
                # have any
                if os.path.splitext(path)[1] == '' and ext is not None:
                    path += '.' + ext
            return Wammu.Locales.ConsoleStrConv(path)
        return None

    def ReadBackup(self, type, data=False):
        filename = self.SelectBackupFile(type, save=False, data=data)
        if filename is None:
            return (None, None)
        try:
            if type == 'message':
                backup = gammu.ReadSMSBackup(filename)
            else:
                backup = gammu.ReadBackup(filename)
        except gammu.GSMError as val:
            info = val.args[0]
            evt = Wammu.Events.ShowMessageEvent(
                message=Wammu.Utils.FormatError(_('Error while reading backup'), info),
                title=_('Error Occured'),
                errortype='gammu',
                type=wx.ICON_ERROR
            )
            wx.PostEvent(self, evt)
            return (None, None)
        return (filename, backup)

    def ReadData(self, evt):
        filename, backup = self.ReadBackup('all', True)
        if backup is None:
            return

        if len(backup['PhonePhonebook']) > 0:
            self.values['contact']['ME'] = map(Wammu.Utils.ParseMemoryEntry, backup['PhonePhonebook'], [self.cfg] * len(backup['PhonePhonebook']))
        if len(backup['SIMPhonebook']) > 0:
            self.values['contact']['SM'] = map(Wammu.Utils.ParseMemoryEntry, backup['SIMPhonebook'], [self.cfg] * len(backup['SIMPhonebook']))
        if len(backup['ToDo']) > 0:
            self.values['todo']['  '] = map(Wammu.Utils.ParseTodo, backup['ToDo'])
        if len(backup['Calendar']) > 0:
            self.values['calendar']['  '] = map(Wammu.Utils.ParseCalendar, backup['Calendar'])

        self.ActivateView('contact', '  ')

        self.SetStatusText(_('Data has been read from file "%s"') % StrConv(filename))

    def ReadSMSData(self, evt):
        filename, backup = self.ReadBackup('message', True)
        if backup is None:
            return

        res = Wammu.Utils.ProcessMessages([[x] for x in backup], False)

        self.values['message']['Sent'] = res['sent']
        self.values['message']['UnSent'] = res['unsent']
        self.values['message']['Read'] = res['read']
        self.values['message']['UnRead'] = res['unread']

        self.ActivateView('message', '  ')

        self.SetStatusText(_('Data has been read from file "%s"') % StrConv(filename))

    def ImportSMS(self, evt):
        filename, backup = self.ReadBackup('message')
        if backup is None:
            return
        choices = []
        values = []
        if len(backup) > 0:
            values.append('message')
            choices.append(_('%d messages') % len(backup))

        if len(values) == 0:
            wx.MessageDialog(
                self,
                _('No importable data were found in file "%s"') % StrConv(filename),
                _('No data to import'),
                wx.OK | wx.ICON_INFORMATION
            ).ShowModal()
            return

        dlg = wx.lib.dialogs.MultipleChoiceDialog(
            self,
            _('Following data was found in backup, select which of these do you want to be added into phone.'),
            _('Select what to import'),
            choices,
            style=wx.CHOICEDLG_STYLE | wx.RESIZE_BORDER,
            size=(600, 200)
        )
        if dlg.ShowModal() != wx.ID_OK:
            return

        lst = dlg.GetValue()
        if len(lst) == 0:
            return

        try:
            busy = wx.BusyInfo(_('Importing data...'))
            time.sleep(0.1)
            wx.Yield()
            for i in lst:
                datatype = values[i]
                if datatype == 'message':
                    smsl = []
                    for v in backup:
                        v['SMSC']['Location'] = 1
                        v['Location'], v['Folder'] = self.sm.AddSMS(v)
                        # reread entry (it doesn't have to contain exactly same data as entered, it depends on phone features)
                        v = self.sm.GetSMS(0, v['Location'])
                        smsl.append(v)

                    res = Wammu.Utils.ProcessMessages(smsl, True)

                    self.values['message']['Sent'] += res['sent']
                    self.values['message']['UnSent'] += res['unsent']
                    self.values['message']['Read'] += res['read']
                    self.values['message']['UnRead'] += res['unread']

                    self.ActivateView('message', '  ')

            del busy
            wx.Yield()

            wx.MessageDialog(
                self,
                _('Backup has been imported from file "%s"') % StrConv(filename),
                _('Backup imported'),
                wx.OK | wx.ICON_INFORMATION
            ).ShowModal()

        except gammu.GSMError as val:
            self.ShowError(val.args[0])

            wx.MessageDialog(
                self,
                _('Restoring from file "%s" has failed, some parts of backup might have been stored to phone and some were not.') % StrConv(filename),
                _('Backup import failed'),
                wx.OK | wx.ICON_INFORMATION
            ).ShowModal()

    def Import(self, evt):
        filename, backup = self.ReadBackup('all')
        if backup is None:
            return
        choices = []
        values = []
        if len(backup['PhonePhonebook']) > 0:
            values.append('PhonePhonebook')
            choices.append(_('%d phone contact entries') % len(backup['PhonePhonebook']))
        if len(backup['SIMPhonebook']) > 0:
            values.append('SIMPhonebook')
            choices.append(_('%d SIM contact entries') % len(backup['SIMPhonebook']))
        if len(backup['ToDo']) > 0:
            values.append('ToDo')
            choices.append(_('%d to do entries') % len(backup['ToDo']))
        if len(backup['Calendar']) > 0:
            values.append('Calendar')
            choices.append(_('%d calendar entries') % len(backup['Calendar']))

        if len(values) == 0:
            wx.MessageDialog(
                self,
                _('No importable data were found in file "%s"') % StrConv(filename),
                _('No data to import'),
                wx.OK | wx.ICON_INFORMATION
            ).ShowModal()
            return

        msg = ''
        if backup['Model'] != '':
            msg = '\n \n' + _('Backup saved from phone %s') % backup['Model']
            if backup['IMEI'] != '':
                msg += _(', serial number %s') % backup['IMEI']
        if backup['Creator'] != '':
            msg += '\n \n' + _('Backup was created by %s') % backup['Creator']
        if backup['DateTime'] is not None:
            msg += '\n \n' + _('Backup saved on %s') % str(backup['DateTime'])

        dlg = wx.lib.dialogs.MultipleChoiceDialog(
            self,
            _('Following data was found in backup, select which of these do you want to be added into phone.') + msg,
            _('Select what to import'),
            choices,
            style=wx.CHOICEDLG_STYLE | wx.RESIZE_BORDER,
            size=(600, 200)
        )
        if dlg.ShowModal() != wx.ID_OK:
            return

        lst = dlg.GetValue()
        if len(lst) == 0:
            return

        try:
            busy = wx.BusyInfo(_('Importing data...'))
            time.sleep(0.1)
            wx.Yield()
            for i in lst:
                datatype = values[i]
                if datatype == 'PhonePhonebook':
                    for v in backup['PhonePhonebook']:
                        v['Location'] = self.sm.AddMemory(v)
                        time.sleep(0.5)
                        # reread entry (it doesn't have to contain exactly same data as entered, it depends on phone features)
                        v = self.sm.GetMemory(v['MemoryType'], v['Location'])
                        Wammu.Utils.ParseMemoryEntry(v, self.cfg)
                        v['Synced'] = True
                        # append new value to list
                        self.values['contact'][v['MemoryType']].append(v)
                    self.ActivateView('contact', 'ME')
                elif datatype == 'SIMPhonebook':
                    for v in backup['SIMPhonebook']:
                        v['Location'] = self.sm.AddMemory(v)
                        time.sleep(0.5)
                        # reread entry (it doesn't have to contain exactly same data as entered, it depends on phone features)
                        v = self.sm.GetMemory(v['MemoryType'], v['Location'])
                        Wammu.Utils.ParseMemoryEntry(v, self.cfg)
                        v['Synced'] = True
                        # append new value to list
                        self.values['contact'][v['MemoryType']].append(v)
                    self.ActivateView('contact', 'SM')
                elif datatype == 'ToDo':
                    for v in backup['ToDo']:
                        v['Location'] = self.sm.AddToDo(v)
                        time.sleep(0.5)
                        # reread entry (it doesn't have to contain exactly same data as entered, it depends on phone features)
                        v = self.sm.GetToDo(v['Location'])
                        Wammu.Utils.ParseTodo(v)
                        v['Synced'] = True
                        # append new value to list
                        self.values['todo']['  '].append(v)
                    self.ActivateView('todo', '  ')
                elif datatype == 'Calendar':
                    for v in backup['Calendar']:
                        v['Location'] = self.sm.AddCalendar(v)
                        time.sleep(0.5)
                        # reread entry (it doesn't have to contain exactly same data as entered, it depends on phone features)
                        v = self.sm.GetCalendar(v['Location'])
                        Wammu.Utils.ParseCalendar(v)
                        v['Synced'] = True
                        # append new value to list
                        self.values['calendar']['  '].append(v)
                    self.ActivateView('calendar', '  ')

            del busy
            wx.Yield()

            wx.MessageDialog(
                self,
                _('Backup has been imported from file "%s"') % StrConv(filename),
                _('Backup imported'),
                wx.OK | wx.ICON_INFORMATION
            ).ShowModal()

        except gammu.GSMError as val:
            self.ShowError(val.args[0])

            wx.MessageDialog(
                self,
                _('Restoring from file "%s" has failed, some parts of backup might have been stored to phone and some were not.') % StrConv(filename),
                _('Backup import failed'),
                wx.OK | wx.ICON_INFORMATION
            ).ShowModal()

    def WriteData(self, evt):
        self.DoBackup(True, 'all')

    def WriteSMSData(self, evt):
        self.DoBackup(True, 'message')

    def Backup(self, evt):
        self.DoBackup(False, 'all')

    def BackupSMS(self, evt):
        self.DoBackup(False, 'message')

    def PrepareBackup(self):
        backup = {}
        backup['Creator'] = 'Wammu ' + Wammu.__version__
        backup['IMEI'] = self.IMEI
        backup['Model'] = '%s %s %s' % (
            self.Manufacturer, self.Model, self.Version
        )
        return backup

    def WriteBackup(self, filename, type, backup, data=False):
        try:
            if type == 'message':
                # Backup is here our internal SMS list: [{'SMS':[{sms1}, {sms2}]}, ...]
                data = [x['SMS'] for x in backup]
                backup = []
                for x in data:
                    backup += x
                gammu.SaveSMSBackup(filename, backup)
            else:
                gammu.SaveBackup(filename, backup)
            if data:
                self.SetStatusText(_('Backup has been saved to file "%s"') % StrConv(filename))
            else:
                self.SetStatusText(_('Data has been saved to file "%s"') % StrConv(filename))
        except gammu.GSMError as val:
            info = val.args[0]
            evt = Wammu.Events.ShowMessageEvent(
                message=Wammu.Utils.FormatError(_('Error while saving backup'), info),
                title=_('Error Occured'),
                errortype='gammu',
                type=wx.ICON_ERROR
            )
            wx.PostEvent(self, evt)
        except MemoryError as val:
            info = val.args[0]
            evt = Wammu.Events.ShowMessageEvent(
                message=_('Error while saving backup, probably some limit inside of Gammu exceeded.\n%s') % str(info),
                title=_('Error Occured'),
                type=wx.ICON_ERROR
            )
            wx.PostEvent(self, evt)

    def DoBackup(self, data, type):
        filename = self.SelectBackupFile(type, data=data)
        if filename is None:
            return
        ext = os.path.splitext(filename)[1].lower()

        if type == 'message':
            backup = (
                self.values['message']['Read'] +
                self.values['message']['UnRead'] +
                self.values['message']['Sent'] +
                self.values['message']['UnSent']
            )
        else:
            backup = self.PrepareBackup()
            if ext in ['.vcf', '.ldif']:
                # these support only one phonebook, so merged it
                backup['PhonePhonebook'] = self.values['contact']['ME'] + self.values['contact']['SM']
            else:
                backup['PhonePhonebook'] = self.values['contact']['ME']
                backup['SIMPhonebook'] = self.values['contact']['SM']

            backup['ToDo'] = self.values['todo']['  ']
            backup['Calendar'] = self.values['calendar']['  ']
        self.WriteBackup(filename, type, backup, data)


    def OnBackup(self, evt):
        filename = self.SelectBackupFile(self.type[0])
        if filename is None:
            return
        ext = os.path.splitext(filename)[1].lower()
        lst = evt.lst
        if self.type[0] == 'message':
            backup = lst
        else:
            backup = self.PrepareBackup()
            if self.type[0] == 'contact':
                if ext in ['.vcf', '.ldif']:
                    # these support only one phonebook, so keep it merged
                    backup['PhonePhonebook'] = lst
                else:
                    sim = []
                    phone = []
                    for item in lst:
                        if item['MemoryType'] == 'SM':
                            sim.append(item)
                        elif  item['MemoryType'] == 'ME':
                            phone.append(item)
                    backup['PhonePhonebook'] = phone
                    backup['SIMPhonebook'] = sim
            elif self.type[0] == 'todo':
                backup['ToDo'] = lst
            elif self.type[0] == 'calendar':
                backup['Calendar'] = lst

        self.WriteBackup(filename, self.type[0], backup)

    def OnDelete(self, evt):
        # first check on supported types
        if self.type[0] not in ['contact', 'call', 'message', 'todo', 'calendar']:
            print 'Delete not yet implemented! (items to delete=%s, type=%s)' % (str(evt.lst), self.type[0])
            return

        lst = evt.lst

        if len(lst) == 0:
            # nothing to delete
            return

        if not lst[0]['Synced']:
            self.OutdatedData()
            return

        # check for confirmation
        if self.cfg.Read('/Wammu/ConfirmDelete') == 'yes':
            count = len(lst)
            if count == 1:
                v = lst[0]
                if self.type[0] == 'contact':
                    txt = _('Are you sure you want to delete contact "%s"?') % v['Name']
                elif self.type[0] == 'call':
                    txt = _('Are you sure you want to delete call from "%s"?') % v['Name']
                elif self.type[0] == 'message':
                    txt = _('Are you sure you want to delete message from "%s"?') % v['Number']
                elif self.type[0] == 'todo':
                    txt = _('Are you sure you want to delete todo entry "%s"?') % v['Text']
                elif self.type[0] == 'calendar':
                    txt = _('Are you sure you want to delete calendar entry "%s"?') % v['Text']
            else:
                if self.type[0] == 'contact':
                    txt = Wammu.Locales.ngettext(
                            'Are you sure you want to delete %d contact?',
                            'Are you sure you want to delete %d contacts?',
                            count) % count
                elif self.type[0] == 'call':
                    txt = Wammu.Locales.ngettext(
                            'Are you sure you want to delete %d call?',
                            'Are you sure you want to delete %d calls?',
                            count) % count
                elif self.type[0] == 'message':
                    txt = Wammu.Locales.ngettext(
                            'Are you sure you want to delete %d message?',
                            'Are you sure you want to delete %d messages?',
                            count) % count
                elif self.type[0] == 'todo':
                    txt = Wammu.Locales.ngettext(
                            'Are you sure you want to delete %d todo entry?',
                            'Are you sure you want to delete %d todo entries?',
                            count) % count
                elif self.type[0] == 'calendar':
                    txt = Wammu.Locales.ngettext(
                            'Are you sure you want to delete %d calendar entry?',
                            'Are you sure you want to delete %d calendar entries?',
                            count) % count
            dlg = wx.MessageDialog(
                self,
                txt,
                _('Confirm deleting'),
                wx.OK | wx.CANCEL | wx.ICON_WARNING
            )
            if dlg.ShowModal() != wx.ID_OK:
                return

        # do real delete
        try:
            if self.type[0] == 'contact' or self.type[0] == 'call':
                busy = wx.BusyInfo(_('Deleting contact(s)...'))
                time.sleep(0.1)
                wx.Yield()
                for v in lst:
                    self.sm.DeleteMemory(v['MemoryType'], v['Location'])
                    for idx in range(len(self.values[self.type[0]][v['MemoryType']])):
                        if self.values[self.type[0]][v['MemoryType']][idx] == v:
                            del self.values[self.type[0]][v['MemoryType']][idx]
                            break
            elif self.type[0] == 'message':
                busy = wx.BusyInfo(_('Deleting message(s)...'))
                time.sleep(0.1)
                wx.Yield()
                for v in lst:
                    for loc in v['Location'].split(', '):
                        self.sm.DeleteSMS(0, int(loc))
                    for idx in range(len(self.values[self.type[0]][v['State']])):
                        if self.values[self.type[0]][v['State']][idx] == v:
                            del self.values[self.type[0]][v['State']][idx]
                            break
            elif self.type[0] == 'todo':
                busy = wx.BusyInfo(_('Deleting todo(s)...'))
                time.sleep(0.1)
                wx.Yield()
                for v in lst:
                    self.sm.DeleteToDo(v['Location'])
                    for idx in range(len(self.values[self.type[0]]['  '])):
                        if self.values[self.type[0]]['  '][idx] == v:
                            del self.values[self.type[0]]['  '][idx]
                            break
            elif self.type[0] == 'calendar':
                busy = wx.BusyInfo(_('Deleting calendar event(s)...'))
                time.sleep(0.1)
                wx.Yield()
                for v in lst:
                    self.sm.DeleteCalendar(v['Location'])
                    for idx in range(len(self.values[self.type[0]]['  '])):
                        if self.values[self.type[0]]['  '][idx] == v:
                            del self.values[self.type[0]]['  '][idx]
                            break
        except gammu.GSMError as val:
            try:
                del busy
            finally:
                self.ShowError(val.args[0])
        except:
            del busy
            raise

        self.ActivateView(self.type[0], self.type[1])

    def OnLink(self, evt):
        v = evt.link.split('://')
        if len(v) != 2:
            print 'Bad URL!'
            return
        if v[0] == 'memory':
            t = v[1].split('/')
            if len(t) != 2:
                print 'Bad URL!'
                return

            if t[0] in ['ME', 'SM']:
                self.ActivateView('contact', t[0])
                try:
                    self.browser.ShowLocation(int(t[1]))
                except KeyError:
                    pass

            elif t[0] in ['MC', 'RC', 'DC']:
                self.ActivateView('call', t[0])
                try:
                    self.browser.ShowLocation(int(t[1]))
                except KeyError:
                    pass

            else:
                print 'Not supported memory type "%s"' % t[0]
                return
        else:
            print 'This link not yet implemented: "%s"' % evt.link

    def OnShowMessage(self, evt):
        try:
            if self.progress.IsShown():
                parent = self.progress
            else:
                parent = self
        except:
            parent = self

        # Is is Gammu error?
        if hasattr(evt, 'errortype') and evt.errortype == 'gammu':
            Wammu.ErrorMessage.ErrorMessage(
                parent,
                StrConv(evt.message),
                StrConv(evt.title)
            ).ShowModal()
        else:
            wx.MessageDialog(
                parent,
                StrConv(evt.message),
                StrConv(evt.title),
                wx.OK | evt.type
            ).ShowModal()

        if hasattr(evt, 'lock'):
            evt.lock.release()

    def ShowInfo(self, event):
        self.ShowProgress(_('Reading phone information'))
        Wammu.Info.GetInfo(self, self.sm).start()
        self.nextfun = self.ActivateView
        self.nextarg = ('info', '  ')

    #
    # Calls
    #

    def ShowCalls(self, event):
        self.GetCallsType('MC')
        self.nextfun = self.ShowCalls2
        self.nextarg = ()

    def ShowCalls2(self):
        self.GetCallsType('DC')
        self.nextfun = self.ShowCalls3
        self.nextarg = ()

    def ShowCalls3(self):
        self.GetCallsType('RC')
        self.nextfun = self.ActivateView
        self.nextarg = ('call', '  ')

    def GetCallsType(self, type):
        self.ShowProgress(_('Reading calls of type %s') % type)
        Wammu.Memory.GetMemory(self, self.sm, 'call', type).start()

    #
    # Contacts
    #

    def ShowContacts(self, event):
        self.GetContactsType('SM')
        self.nextfun = self.ShowContacts2
        self.nextarg = ()

    def ShowContacts2(self):
        self.GetContactsType('ME')
        self.nextfun = self.ActivateView
        self.nextarg = ('contact', '  ')

    def ShowContactsME(self, event):
        self.GetContactsType('ME')
        self.nextfun = self.ActivateView
        self.nextarg = ('contact', 'ME')

    def ShowContactsSM(self, event):
        self.GetContactsType('SM')
        self.nextfun = self.ActivateView
        self.nextarg = ('contact', 'SM')

    def GetContactsType(self, type):
        self.ShowProgress(_('Reading contacts from %s') % type)
        Wammu.Memory.GetMemory(self, self.sm, 'contact', type).start()

    #
    # Messages
    #

    def ShowMessages(self, event):
        self.ShowProgress(_('Reading messages'))
        Wammu.Message.GetMessage(self, self.sm).start()
        self.nextfun = self.ActivateView
        self.nextarg = ('message', '  ')

    #
    # Todos
    #

    def ShowTodos(self, event):
        self.ShowProgress(_('Reading todos'))
        Wammu.Todo.GetTodo(self, self.sm).start()
        self.nextfun = self.ActivateView
        self.nextarg = ('todo', '  ')

    #
    # Calendars
    #

    def ShowCalendar(self, event):
        self.ShowProgress(_('Reading calendar'))
        Wammu.Calendar.GetCalendar(self, self.sm).start()
        self.nextfun = self.ActivateView
        self.nextarg = ('calendar', '  ')

    #
    # Get everything
    #

    def GetAll(self, event):
        self.ShowProgress(_('Reading phone information'))
        Wammu.Info.GetInfo(self, self.sm).start()
        self.nextfun = self.GetAll2
        self.nextarg = ()

    def GetAll2(self):
        self.GetContactsType('SM')
        self.nextfun = self.GetAll3
        self.nextarg = ()

    def GetAll3(self):
        self.GetContactsType('ME')
        self.nextfun = self.GetAll4
        self.nextarg = ()

    def GetAll4(self):
        self.GetCallsType('MC')
        self.nextfun = self.GetAll5
        self.nextarg = ()

    def GetAll5(self):
        self.GetCallsType('DC')
        self.nextfun = self.GetAll6
        self.nextarg = ()

    def GetAll6(self):
        self.GetCallsType('RC')
        self.nextfun = self.GetAll7
        self.nextarg = ()

    def GetAll7(self):
        self.ShowProgress(_('Reading messages'))
        Wammu.Message.GetMessage(self, self.sm).start()
        self.nextfun = self.GetAll8
        self.nextarg = ()

    def GetAll8(self):
        self.ShowProgress(_('Reading todos'))
        Wammu.Todo.GetTodo(self, self.sm).start()
        self.nextfun = self.GetAll9
        self.nextarg = ()

    def GetAll9(self):
        self.ShowProgress(_('Reading calendar'))
        Wammu.Calendar.GetCalendar(self, self.sm).start()
        self.nextfun = self.ActivateView
        self.nextarg = ('info', '  ')

    #
    # Time
    #

    def SyncTime(self, event):
        busy = wx.BusyInfo(_('Setting time in phone...'))
        time.sleep(0.1)
        wx.Yield()
        try:
            self.sm.SetDateTime(datetime.datetime.now())
        except gammu.GSMError as val:
            del busy
            self.ShowError(val.args[0])
        except:
            del busy
            raise

    #
    # Files
    #

    def SendFile(self, event):
        '''
        Sends file to phone.

        @todo: Maybe we could add some wildcards for commonly used file types.
        '''
        dlg = wx.FileDialog(
            self,
            _('Send file to phone'),
            os.getcwd(),
            '',
            _('All files') + ' (*.*)|*.*',
            wx.OPEN | wx.CHANGE_DIR
        )
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            try:
                file_data = open(path, 'r').read()
                file_f = {
                    'ID_FullName': '',
                    'Name': os.path.basename(path),
                    'Folder': 0,
                    'Level': 1,
                    'Used': len(file_data),
                    'Buffer': file_data,
                    'Type': 'Other',
                    'Protected': 0,
                    'ReadOnly': 0,
                    'Hidden': 0,
                    'System': 0,
                    'Handle': 0,
                    'Pos': 0,
                    'Finished': 0
                }
                busy = wx.BusyInfo(_('Sending file to phone...'))
                time.sleep(0.1)
                wx.Yield()
                try:
                    while (not file_f['Finished']):
                        file_f = self.sm.SendFilePart(file_f)
                except gammu.ERR_PERMISSION:
                    wx.MessageDialog(
                        self,
                        _('Transfer has been rejected by phone.'),
                        _('Transfer rejected!'),
                        wx.OK | wx.ICON_ERROR
                    ).ShowModal()
                except gammu.GSMError as val:
                    del busy
                    self.ShowError(val.args[0])
                except:
                    del busy
                    raise
            except IOError:
                wx.MessageDialog(
                    self,
                    _('Selected file "%s" was not found, no data read.') % path,
                    _('File not found!'),
                    wx.OK | wx.ICON_ERROR
                ).ShowModal()

    #
    # Connecting / Disconnecting
    #

    def PhoneConnect(self, event=None):
        busy = wx.BusyInfo(_('One moment please, connecting to phone...'))
        time.sleep(0.1)
        wx.Yield()
        section = self.cfg.ReadInt('/Gammu/Section')
        config = self.cfg.gammu.GetConfig(section)
        if config['Connection'] == '' or config['Device'] == '':
            wx.MessageDialog(
                self,
                _('Phone connection is not properly configured, can not connect to phone.'),
                _('Connection not configured!'),
                wx.OK | wx.ICON_ERROR
            ).ShowModal()
            return
        cfg = {
            'StartInfo': self.cfg.ReadBool('/Gammu/StartInfo'),
            'UseGlobalDebugFile': True,
            'DebugFile': None, # Set on other place
            'SyncTime': self.cfg.ReadBool('/Gammu/SyncTime'),
            'Connection': config['Connection'],
            'LockDevice': self.cfg.ReadBool('/Gammu/LockDevice'),
            'DebugLevel': 'textalldate', # Set on other place
            'Device': config['Device'],
            'Model': config['Model'],
            }

        # Store configuration for error handling
        self.gammu_config = cfg

        # Compatibility with old Gammu versions
        cfg = Wammu.Utils.CompatConfig(cfg)

        self.sm.SetConfig(0, cfg)
        try:
            self.sm.Init()
            self.sm.SetIncomingCallback(self.IncomingEvent)
            try:
                self.sm.SetIncomingCall(True)
            except gammu.GSMError:
                pass
            self.TogglePhoneMenus(True)
            self.SetupNumberPrefix()
            try:
                self.IMEI = self.sm.GetIMEI()
            except gammu.GSMError:
                pass
            try:
                self.Manufacturer = self.sm.GetManufacturer()
                self.cfg.Write('/Phone-0/Manufacturer', self.Manufacturer)
            except gammu.GSMError:
                pass
            try:
                m = self.sm.GetModel()
                if m[0] == '' or m[0] == 'unknown':
                    self.Model = m[1]
                else:
                    self.Model = m[0]
                self.cfg.Write('/Phone-0/Model', self.Model)
            except gammu.GSMError:
                pass
            try:
                self.Version = self.sm.GetFirmware()[0]
            except:
                pass

        except gammu.GSMError as val:
            del busy
            self.ShowError(val.args[0])
            try:
                self.sm.Terminate()
            except gammu.GSMError as val:
                pass
        except:
            del busy
            raise

        # Check for PIN
        if self.connected:
            try:
                code = self.sm.GetSecurityStatus()
            except gammu.GSMError:
                code = None
            if code is not None:
                dlg = wx.PasswordEntryDialog(
                    self,
                    _('Please enter %s code:') % code,
                    _('Phone asks for security code')
                )
                if dlg.ShowModal() == wx.ID_OK:
                    self.sm.EnterSecurityCode(code, dlg.GetValue())


    def DBUSActionCallback(self, id, action):
        '''
        Called when user does something on notification.
        '''
        self.dbus_notify.CloseNotification(self.last_dbus_id)
        if action == 'accept-call':
            self.sm.AnswerCall(0, True)
        elif action == 'reject-call':
            self.sm.CancelCall(0, True)
        else:
            print 'Unknown DBUS event: %s' % action

    def DBUSNotify(self, title, message, actions):
        '''
        Performs D-Bus notification if available.
        '''
        if self.dbus_notify is not None:
            try:
                self.last_dbus_id = self.dbus_notify.Notify(
                        'Wammu', self.last_dbus_id, 'wammu',
                        title, message, actions, {}, -1)
            except dbus.DBusException:
                self.dbus_notify = None
                self.last_dbus_id = 0

    def IncomingEvent(self, sm, type, data):
        '''
        Called on incoming event from phone.
        '''

        if type == 'Call':
            if data['Status'] != 'IncomingCall':
                # We care only about incoming calls
                return
            if data['Number'] == '':
                msg = _('Your phone has just received incoming call')
            else:
                msg = _('Your phone has just received incoming call from %s') % data['Number']
            self.DBUSNotify(
                _('Incoming call'),
                msg,
                ['reject-call', _('Reject'), 'accept-call', _('Accept')]
            )

    def PhoneDisconnect(self, event=None):
        busy = wx.BusyInfo(_('One moment please, disconnecting from phone...'))
        time.sleep(0.1)
        wx.Yield()
        try:
            self.sm.Terminate()
        except gammu.ERR_NOTCONNECTED:
            del busy
            pass
        except gammu.GSMError as val:
            del busy
            self.ShowError(val.args[0])
        except:
            del busy
            raise
        self.TogglePhoneMenus(False)

    def SearchMessage(self, text):
        """
        This has to send message as it is called from different thread.
        """
        evt = Wammu.Events.TextEvent(text=text + '\n')
        wx.PostEvent(self.searchlog, evt)

    def SearchDone(self, lst):
        """
        This has to send message as it is called from different thread.
        """
        self.founddevices = lst
        evt = Wammu.Events.DoneEvent()
        wx.PostEvent(self.searchlog, evt)

    def SearchPhone(self, evt=None):
        if self.connected:
            wx.MessageDialog(
                self,
                _('Searching for phone can not be performed while you are connected to phone, please disconnect first.'),
                _('You are connected to phone!'),
                wx.OK | wx.ICON_ERROR
            ).ShowModal()
            return

        index = self.cfg.gammu.FirstFree()
        result = Wammu.PhoneWizard.RunConfigureWizard(self, index)
        if result is not None:
            self.cfg.gammu.SetConfig(result['Position'], result['Device'], result['Connection'], result['Name'])
            self.cfg.WriteInt('/Gammu/Section', index)

    def About(self, evt=None):
        Wammu.About.AboutBox(self).ShowModal()

    def Website(self, evt=None):
        Wammu.Webbrowser.Open("http://%swammu.eu/?version=%s" % (Wammu.Utils.GetWebsiteLang(), Wammu.__version__))

    def Support(self, evt=None):
        Wammu.Webbrowser.Open("http://%swammu.eu/support/?version=%s" % (Wammu.Utils.GetWebsiteLang(), Wammu.__version__))

    def ReportBug(self, evt=None):
        Wammu.Webbrowser.Open("https://github.com/gammu/wammu/issues")

    def PhoneDB(self, evt=None):
        Wammu.Webbrowser.Open("http://%swammu.eu/phones/" % Wammu.Utils.GetWebsiteLang())

    def Talkback(self, evt=None):
        Wammu.TalkbackDialog.DoTalkback(self, self.cfg, 0)

    def Donate(self, evt=None):
        Wammu.Webbrowser.Open("http://%swammu.eu/donate/?src=wammu" % Wammu.Utils.GetWebsiteLang())

    def SaveLog(self, evt=None):
        '''
        Saves debug log to file.
        '''
        dlg = wx.FileDialog(
            self,
            _('Save debug log as...'),
            os.getcwd(),
            'wammu.log',
            '',
            wx.SAVE | wx.OVERWRITE_PROMPT | wx.CHANGE_DIR
        )
        if dlg.ShowModal() == wx.ID_OK:
            Wammu.ErrorLog.SaveLog(filename=dlg.GetPath())
