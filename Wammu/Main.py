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
Main Wammu window
'''

import wx
import wx.html
import gammu
import sys
import os
import os.path
import time
import datetime
import string
import locale
import Wammu
import Wammu.Events
import Wammu.Displayer
import Wammu.Browser
import Wammu.Editor
import Wammu.Info
import Wammu.Utils
import Wammu.Message
import Wammu.Memory
import Wammu.Todo
import Wammu.Calendar
import Wammu.Logger
import Wammu.Settings
from Wammu.Paths import *
import threading
import copy
import wx.lib.wxpTag
import wx.lib.dialogs
import Wammu.Data
import Wammu.Composer
import Wammu.MessageDisplay
import Wammu.PhoneSearch
import Wammu.About
from Wammu.Utils import StrConv, Str_ as _

def SortDataKeys(a, b):
    if a == 'info':
        return -1
    elif b == 'info':
        return 1
    else:
        return cmp(a,b)
        
def SortDataSubKeys(a, b):
    if a == '  ':
        return -1
    elif b == '  ':
        return 1
    else:
        return cmp(a,b)

displaydata = {}
displaydata['info'] = {}
displaydata['call'] = {}
displaydata['contact'] = {}
displaydata['message'] = {}
displaydata['todo'] = {}
displaydata['calendar'] = {}

#information
displaydata['info']['  '] = ('', _('Phone'), _('Phone Information'), 'phone', [[_('Wammu version'), Wammu.__version__], [_('Gammu version'), gammu.Version()[0]], [_('python-gammu version'), gammu.Version()[1]]])

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

#todos
displaydata['todo']['  '] = ('info', _('Todos'), _('All Todo Items'), 'todo', [])

#calendar
displaydata['calendar']['  '] = ('info', _('Calendar'), _('All Calendar Events'), 'calendar', [])


## Create a new frame class, derived from the wxPython Frame.
class WammuFrame(wx.Frame):

    def __init__(self, parent, id):
        self.cfg = wx.Config(style = wx.CONFIG_USE_LOCAL_FILE)
        if self.cfg.HasEntry('/Main/X') and self.cfg.HasEntry('/Main/Y'):
            pos = wx.Point(self.cfg.ReadInt('/Main/X', 0), self.cfg.ReadInt('/Main/Y', 0))
        else:
            pos =wx.DefaultPosition
        size = wx.Size(self.cfg.ReadInt('/Main/Width', 640), self.cfg.ReadInt('/Main/Height', 480))

        wx.Frame.__init__(self, parent, id, 'Wammu', pos, size, wx.DEFAULT_FRAME_STYLE)
        self.CreateStatusBar(2)
        self.SetStatusWidths([-1,100])

        # Associate some events with methods of this class
        wx.EVT_CLOSE(self, self.CloseWindow)
        Wammu.Events.EVT_PROGRESS(self, self.OnProgress)
        Wammu.Events.EVT_SHOW_MESSAGE(self, self.OnShowMessage)
        Wammu.Events.EVT_LINK(self, self.OnLink)
        Wammu.Events.EVT_DATA(self, self.OnData)
        Wammu.Events.EVT_SHOW(self, self.OnShow)
        Wammu.Events.EVT_EDIT(self, self.OnEdit)
        Wammu.Events.EVT_SEND(self, self.OnSend)
        Wammu.Events.EVT_DUPLICATE(self, self.OnDuplicate)
        Wammu.Events.EVT_REPLY(self, self.OnReply)
        Wammu.Events.EVT_DELETE(self, self.OnDelete)
        Wammu.Events.EVT_BACKUP(self, self.OnBackup)

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
        

        # right frame
        self.rightsplitter = wx.SplitterWindow(self.splitter, -1)
        self.rightwin = wx.Panel(self.rightsplitter, -1)
        self.rightwin.sizer = wx.BoxSizer(wx.VERTICAL)
        
        # title text
        self.label = wx.StaticText(self.rightwin, -1, 'Wammu')
        self.rightwin.sizer.Add(self.label, 0, wx.LEFT|wx.ALL|wx.EXPAND, 2)

        # line
        self.rightwin.sizer.Add(wx.StaticLine(self.rightwin, -1), 0 , wx.EXPAND)

        # item browser
        self.browser = Wammu.Browser.Browser(self.rightwin, self)
        self.rightwin.sizer.Add(self.browser, 1, wx.EXPAND)
        self.rightwin.SetSizer(self.rightwin.sizer)

        # values displayer
        self.content = Wammu.Displayer.Displayer(self.rightsplitter, self)

        self.rightsplitter.SplitHorizontally(self.rightwin, self.content, self.cfg.ReadInt('/Main/SplitRight', -200))

        self.splitter.SplitVertically(self.tree, self.rightsplitter, self.cfg.ReadInt('/Main/Split', 160))

        # initial content
        self.content.SetPage('<body><html><font size=+1><b>' + _('Welcome to Wammu') + ' ' + Wammu.__version__ + 
        '</b></font></html></body>')

        # Prepare the menu bar
        self.menuBar = wx.MenuBar()

        menu1 = wx.Menu()
        menu1.Append(101, _('&SearchPhone'), _('Search for phone'))
        menu1.AppendSeparator()
        menu1.Append(150, _('&Settings'), _('Change Wammu settings'))
        menu1.AppendSeparator()
        menu1.Append(199, _('E&xit'), _('Exit Wammu'))
        # Add menu to the menu bar
        self.menuBar.Append(menu1, _('&Wammu'))
        
        menu2 = wx.Menu()
        menu2.Append(201, _('&Connect'), _('Connect the device'))
        menu2.Append(202, _('&Disconnect'), _('Disconnect the device'))
        menu2.AppendSeparator()
        menu2.Append(210, _('&Synchronise time'), _('Synchronises time in mobile with PC'))
        # Add menu to the menu bar
        self.menuBar.Append(menu2, _('&Phone'))

        menu3 = wx.Menu()
        menu3.Append(301, _('&Info'), _('Get phone information'))
        menu3.AppendSeparator()
        menu3.Append(310, _('Contacts (&SIM)'), _('Contacts from SIM'))
        menu3.Append(311, _('Contacts (&phone)'), _('Contacts from phone memory'))
        menu3.Append(312, _('&Contacts (All)'), _('Contacts from phone and SIM memory'))
        menu3.AppendSeparator()
        menu3.Append(320, _('C&alls'), _('Calls'))
        menu3.AppendSeparator()
        menu3.Append(330, _('&Messages'), _('Messages'))
        menu3.AppendSeparator()
        menu3.Append(340, _('&Todos'), _('Todos'))
        menu3.AppendSeparator()
        menu3.Append(350, _('Calenda&r'), _('Calendar'))
        # Add menu to the menu bar
        self.menuBar.Append(menu3, _('&Retrieve'))

        menu4 = wx.Menu()
        menu4.Append(401, _('&Contact'), _('Crates new contact'))
        menu4.Append(402, _('Calendar &event'), _('Crates new calendar event'))
        menu4.Append(403, _('&Todo'), _('Crates new todo'))
        menu4.Append(404, _('&Message'), _('Crates new message'))
        # Add menu to the menu bar
        self.menuBar.Append(menu4, _('&New'))

        menu5 = wx.Menu()
        menu5.Append(501, _('&Save'), _('Saves currently retrieved data to backup'))
        menu5.Append(502, _('&Import'), _('Imports data from backup to phone'))
        # Add menu to the menu bar
        self.menuBar.Append(menu5, _('&Backups'))

        menuhelp = wx.Menu()
        menuhelp.Append(1001, _('&About'), _('Information about program'))
        # Add menu to the menu bar
        self.menuBar.Append(menuhelp, _('&Help'))

        # Set menu bar
        self.SetMenuBar(self.menuBar)

        # menu events
        wx.EVT_MENU(self, 101, self.SearchPhone)
        wx.EVT_MENU(self, 150, self.Settings)
        wx.EVT_MENU(self, 199, self.CloseWindow)
        
        wx.EVT_MENU(self, 201, self.PhoneConnect)
        wx.EVT_MENU(self, 202, self.PhoneDisconnect)
        wx.EVT_MENU(self, 210, self.SyncTime)

        wx.EVT_MENU(self, 301, self.ShowInfo)
        wx.EVT_MENU(self, 310, self.ShowContactsSM)
        wx.EVT_MENU(self, 311, self.ShowContactsME)
        wx.EVT_MENU(self, 312, self.ShowContacts)
        wx.EVT_MENU(self, 320, self.ShowCalls)
        wx.EVT_MENU(self, 330, self.ShowMessages)
        wx.EVT_MENU(self, 340, self.ShowTodos)
        wx.EVT_MENU(self, 350, self.ShowCalendar)
        
        wx.EVT_MENU(self, 401, self.NewContact)
        wx.EVT_MENU(self, 402, self.NewCalendar)
        wx.EVT_MENU(self, 403, self.NewTodo)
        wx.EVT_MENU(self, 404, self.NewMessage)

        wx.EVT_MENU(self, 501, self.Backup)
        wx.EVT_MENU(self, 502, self.Import)
        
        wx.EVT_MENU(self, 1001, self.About)

        self.TogglePhoneMenus(False)

        self.type = ['info','  ']
        self.ActivateView('info', '  ')
        
        # create state machine
        self.sm = gammu.StateMachine()

        self.showdebug = ''


    def PostInit(self):
        # things that need window opened
        if not self.cfg.HasGroup('/Gammu'):
            try:
                self.sm.ReadConfig()
                config = self.sm.GetConfig()

                wx.MessageDialog(self, 
                    _('Wammu configuration was not found. Gammu settings were read and will be used as defaults.') + '\n' +
                    _('You will now be taken to configuration dialog to check configuration.'),
                    _('Configuration not found'),
                    wx.OK | wx.ICON_INFORMATION).ShowModal()
            except:
                config = {}
                dlg = wx.MessageDialog(self,
                    _('Wammu configuration was not found and Gammu settings couldn\'t be read.') + '\n\n' + 
                    _('Wammu can now try to search for phone. Do you want Wammu to search for phone?') + '\n' +
                    _('After searching you will now be taken to configuration dialog to check whether it was detected correctly.') + '\n\n' +
                    _('If you press cancel, no searching will be performed.'),
                    _('Configuration not found'),
                    wx.OK | wx.CANCEL | wx.ICON_WARNING)
                if dlg.ShowModal() == wx.ID_OK:
                    self.SearchPhone()
                    config['Model'] = self.cfg.Read('/Gammu/Model', Wammu.Models[0])
                    config['Connection'] = self.cfg.Read('/Gammu/Connection', Wammu.Connections[0])
                    config['Device'] = self.cfg.Read('/Gammu/Device', Wammu.Devices[0])
                    
            # make some defaults
            if not config.has_key('Model') or config['Model'] == None:
                config['Model'] = Wammu.Models[0]
            if not config.has_key('Connection') or config['Connection'] == None:
                config['Connection'] = Wammu.Connections[0]
            if not config.has_key('Device') or config['Device'] == None:
                config['Device'] = Wammu.Devices[0]
            if not config.has_key('SyncTime') or not config['SyncTime'] == 'yes':
                config['SyncTime'] = 'no'
            if not config.has_key('LockDevice') or not config['LockDevice'] == 'yes':
                config['LockDevice'] = 'no'
            if not config.has_key('StartInfo') or not config['StartInfo'] == 'yes':
                config['StartInfo'] = 'no'

            self.cfg.Write('/Gammu/Model', config['Model'])
            self.cfg.Write('/Gammu/Device', config['Device'])
            self.cfg.Write('/Gammu/Connection', config['Connection'])
            self.cfg.Write('/Gammu/SyncTime', config['SyncTime'])
            self.cfg.Write('/Gammu/LockDevice', config['LockDevice'])
            self.cfg.Write('/Gammu/StartInfo', config['StartInfo'])

            self.Settings()
        else:
            self.DoDebug(self.cfg.Read('/Debug/Show', 'no'))

        if (self.cfg.Read('/Wammu/AutoConnect', 'no') == 'yes'):
            self.PhoneConnect()


    def DoDebug(self, newdebug):
        if newdebug != self.showdebug:
            self.showdebug = newdebug
            if self.showdebug == 'yes':
                gammu.SetDebugFile(sys.stderr)
                gammu.SetDebugLevel('textall')
                self.sm.SetDebugLevel('textall')
            else:
                gammu.SetDebugFile(None)
                gammu.SetDebugLevel('nothing')
                self.sm.SetDebugLevel('nothing')

#            if hasattr(self, 'piper'):
#                gammu.SetDebugFile(None)
#                self.logger.canceled = True
#                del self.logger
#                self.SaveWinSize(self.logwin, '/Debug')
#                self.logwin.Destroy()
#                self.pipew.write('\n')
#                del self.logwin
#                del self.piper
#                del self.pipew
#
#            if self.showdebug == 'yes':
#                piper, pipew = os.pipe()
#                self.piper = os.fdopen(piper, 'r')
#                self.pipew = os.fdopen(pipew, 'w')
#                gammu.SetDebugFile(self.pipew)
#                self.sm.SetDebugLevel('textall')
#                self.logwin = Wammu.Logger.LogFrame(self, self.cfg)
#                self.logwin.Show(True)
#                wx.EVT_CLOSE(self.logwin, self.LogClose)
#                self.logger = Wammu.Logger.Logger(self.logwin, self.piper)
#                self.logger.start()
                
    def SaveWinSize(self, win, key):
        x,y = win.GetPositionTuple()
        w,h = win.GetSizeTuple()
        
        self.cfg.WriteInt(key + '/X', x)
        self.cfg.WriteInt(key + '/Y', y)
        self.cfg.WriteInt(key + '/Width', w)
        self.cfg.WriteInt(key + '/Height', h)
        

    def LogClose(self, evt):
        self.SaveWinSize(self.logwin, '/Debug')
        self.cfg.Write('/Debug/Show', 'no')
        self.DoDebug('no')

    def TogglePhoneMenus(self, enable):
        self.connected = enable
        if enable:
            self.SetStatusText(_('Connected'), 1)
        else:
            self.SetStatusText(_('Disconnected'), 1)
        mb = self.menuBar

        mb.Enable(201, not enable);
        mb.Enable(202, enable);
        
        mb.Enable(210, enable);

        mb.Enable(301, enable);

        mb.Enable(310, enable);
        mb.Enable(311, enable);
        mb.Enable(312, enable);
        
        mb.Enable(320, enable);
        
        mb.Enable(330, enable);
        
        mb.Enable(340, enable);
        
        mb.Enable(350, enable);
        
        mb.Enable(401, enable);
        mb.Enable(402, enable);
        mb.Enable(403, enable);
        mb.Enable(404, enable);
        
        mb.Enable(501, enable);
        mb.Enable(502, enable);

    def ActivateView(self, k1, k2):
        self.tree.SelectItem(self.treei[k1][k2])
        self.ChangeView(k1, k2)

    def ChangeView(self, k1, k2):
        self.ChangeBrowser(k1, k2)
        self.label.SetLabel(displaydata[k1][k2][2])

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

    def Settings(self, event = None):
        result = Wammu.Settings.Settings(self, self.cfg).ShowModal()
        if result == wx.ID_OK:
            if self.connected:
                wx.MessageDialog(self, 
                    _('If you changed parameters affecting phone connection, they will be used next time you connect to phone.'),
                    _('Notice'),
                    wx.OK | wx.ICON_INFORMATION).ShowModal()
            self.DoDebug(self.cfg.Read('/Debug/Show', 'no'))

    def CloseWindow(self, event):
        self.SaveWinSize(self, '/Main')
        self.cfg.WriteInt('/Main/Split', self.splitter.GetSashPosition())
        self.cfg.WriteInt('/Main/SplitRight', self.rightsplitter.GetSashPosition())
        
        self.DoDebug('no')
        # tell the window to kill itself
        self.Destroy()

    def ShowError(self, info):
        evt = Wammu.Events.ShowMessageEvent(
            message = _('Got error from phone:\n%s\nIn:%s\nError code: %d') % (info['Text'], info['Where'], info['Code']),
            title = _('Error Occured'),
            type = wx.ICON_ERROR)
        wx.PostEvent(self, evt)

    def ShowProgress(self, text):
        self.progress = wx.ProgressDialog(
                        _('Operation in progress'),
                        text,
                        100,
                        self,
                        wx.PD_CAN_ABORT | wx.PD_APP_MODAL | wx.PD_AUTO_HIDE | wx.PD_ELAPSED_TIME | wx.PD_REMAINING_TIME | wx.PD_ESTIMATED_TIME)

    def OnData(self, evt):
        self.values[evt.type[0]][evt.type[1]] = evt.data
        if evt.last and hasattr(self, 'nextfun'):
            f = self.nextfun
            a = self.nextarg
            del self.nextfun
            del self.nextarg
            f (*a)

    def ShowData(self, data):
        text = ''
        for d in data:
            if len(d) == 2:
                text = text + ('<b>%s</b>: %s<br>' % (d[0], d[1]))
            else:
                text = text + ('<br>%s' % d[0])
        if wx.USE_UNICODE:
            self.content.SetPage(u'<html><head><meta http-equiv="Content-Type" content="text/html; charset=ucs-2"></head><body>%s</body></html>' % StrConv(text))
        else:
            try:
                loc = locale.getdefaultlocale()
                charset = loc[1]
            except:
                charset = 'iso-8859-1'
            self.content.SetPage('<html><head><meta http-equiv="Content-Type" content="text/html; charset=%s"></head><body>%s</body></html>' % (charset, StrConv(text)))
            
    def OnShow(self, evt): 
        if self.type == ['info','  ']:
            data = [self.values['info']['__'][evt.index]]
        elif self.type[0] == 'contact' or self.type[0] == 'call':
            if self.type[1] == '  ':
                t = '__'
            else:
                t = self.type[1]
            v = self.values[self.type[0]][t][evt.index]
            data = [
                (_('Location'), str(v['Location'])),
                (_('Memory type'), v['MemoryType'])]
            for i in v['Entries']:
                data.append((i['Type'], Wammu.Utils.GetTypeString(i['Type'], i['Value'], self.values, linkphone = False)))
        elif self.type[0] == 'message':
            text = ''
            if self.type[1] == '  ':
                t = '__'
            else:
                t = self.type[1]
            v = self.values[self.type[0]][t][evt.index]
            data = [
                (_('Number'), Wammu.Utils.GetNumberLink([] + self.values['contact']['ME'] + self.values['contact']['SM'], v['Number'])),
                (_('Date'), StrConv(v['DateTime'])),
                (_('Location'), StrConv(v['Location'])),
                (_('Folder'), StrConv(v['SMS'][0]['Folder'])),
                (_('Memory'), StrConv(v['SMS'][0]['Memory'])),
                (_('SMSC'), Wammu.Utils.GetNumberLink([] + self.values['contact']['ME'] + self.values['contact']['SM'], v['SMS'][0]['SMSC']['Number'])),
                (_('State'), StrConv(v['State']))]
            if v['Name'] != '':
                data.append((_('Name'), StrConv(v['Name'])))
            data.append((Wammu.MessageDisplay.SmsToHtml(self.cfg, v),))
        elif self.type[0] == 'todo':
            if self.type[1] == '  ':
                t = '__'
            else:
                t = self.type[1]
            v = self.values[self.type[0]][t][evt.index]
            data = [
                (_('Location'), str(v['Location'])),
                (_('Priority'), v['Priority'])]
            for i in v['Entries']:
                data.append((i['Type'], Wammu.Utils.GetTypeString(i['Type'], i['Value'], self.values)))
        elif self.type[0] == 'calendar':
            if self.type[1] == '  ':
                t = '__'
            else:
                t = self.type[1]
            v = self.values[self.type[0]][t][evt.index]
            data = [
                (_('Location'), str(v['Location'])),
                (_('Type'), v['Type'])]
            for i in v['Entries']:
                data.append((i['Type'], Wammu.Utils.GetTypeString(i['Type'], i['Value'], self.values)))
        else:
            data = [('Show not yet implemented! (id = %d)' % evt.index,)]
        self.ShowData(data)

    def NewContact(self, evt):
        self.EditContact({})

    def NewCalendar(self, evt):
        self.EditCalendar({})

    def NewTodo(self, evt):
        self.EditTodo({})
    
    def NewMessage(self, evt):
        self.ComposeMessage({})

    def ComposeMessage(self, v):
        if Wammu.Composer.SMSComposer(self, self.cfg, v, self.values).ShowModal() == wx.ID_OK:
            v['SMS'] = gammu.EncodeSMS(v['SMSInfo'])
            if v['Save']:
                result = {}
                result['SMS'] = []
                
            for msg in v['SMS']:
                msg['SMSC']['Location'] = 1

                msg['Folder'] = v['Folder']
                msg['Number'] = v['Number']
                msg['Type'] = v['Type']
                msg['State'] = v['State']

                busy = wx.BusyInfo(_('Writing message...'))
                try:
                    if v['Save']:
                        msg['Location'] = self.sm.AddSMS(msg)
                        if v['Send']:
                            self.sm.SendSavedSMS(msg['Folder'], msg['Location'])
                        result['SMS'].append(self.sm.GetSMS(msg['Folder'], msg['Location'])[0])
                    elif v['Send']:
                        msg['MessageReference'] = self.sm.SendSMS(msg)
                except gammu.GSMError, val:
                    self.ShowError(val[0])
                del busy
                
            if v['Save']:
                info = gammu.DecodeSMS(result['SMS'])
                if info != None:
                    result['SMSInfo'] = info
                Wammu.Utils.ParseMessage(result, (info != None))
                self.values['message'][result['State']].append(result)
                self.ActivateView('message', result['State'])
                try:
                    self.browser.ShowLocation(result['Location'])
                except KeyError:
                    pass

    def EditContact(self, v):
        backup = copy.deepcopy(v)
        shoulddelete = (v == {} or v['Location'] == 0)
        if Wammu.Editor.ContactEditor(self, self.cfg, self.values, v).ShowModal() == wx.ID_OK:
            try:
                busy = wx.BusyInfo(_('Writing contact...'))
                # was entry moved => delete it
                if not shoulddelete:
                    # delete from internal list
                    for idx in range(len(self.values['contact'][backup['MemoryType']])):
                        if self.values['contact'][backup['MemoryType']][idx] == v:
                            del self.values['contact'][backup['MemoryType']][idx]
                            break

                    if v['MemoryType'] != backup['MemoryType'] or  v['Location'] != backup['Location']:
                        # delete from phone
                        self.sm.DeleteMemory(backup['MemoryType'], backup['Location'])

                # have we specified location? => add or set
                if v['Location'] == 0:
                    v['Location'] = self.sm.AddMemory(v)
                else:
                    v['Location'] = self.sm.SetMemory(v)

                # reread entry (it doesn't have to contain exactly same data as entered, it depends on phone features)
                v = self.sm.GetMemory(v['MemoryType'], v['Location'])
                Wammu.Utils.ParseMemoryEntry(v)
                # append new value to list
                self.values['contact'][v['MemoryType']].append(v)

            except gammu.GSMError, val:
                v = backup
                self.ShowError(val[0])

            if (self.type[0] == 'contact' and self.type[1] == '  ') or not v.has_key('MemoryType'):
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
                # was entry moved => delete it
                if not shoulddelete:
                    # delete from internal list
                    for idx in range(len(self.values['calendar']['  '])):
                        if self.values['calendar']['  '][idx] == v:
                            del self.values['calendar']['  '][idx]
                            break

                    if v['Location'] != backup['Location']:
                        # delete from phone
                        self.sm.DeleteCalendar(backup['Location'])

                # have we specified location? => add or set
                if v['Location'] == 0:
                    v['Location'] = self.sm.AddCalendar(v)
                else:
                    v['Location'] = self.sm.SetCalendar(v)

                # reread entry (it doesn't have to contain exactly same data as entered, it depends on phone features)
                v = self.sm.GetCalendar(v['Location'])
                Wammu.Utils.ParseCalendar(v)
                # append new value to list
                self.values['calendar']['  '].append(v)

            except gammu.GSMError, val:
                v = backup
                self.ShowError(val[0])

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
                # was entry moved => delete it
                if not shoulddelete:
                    # delete from internal list
                    for idx in range(len(self.values['todo']['  '])):
                        if self.values['todo']['  '][idx] == v:
                            del self.values['todo']['  '][idx]
                            break

                    if v['Location'] != backup['Location']:
                        # delete from phone
                        self.sm.DeleteToDo(backup['Location'])

                # have we specified location? => add or set
                if v['Location'] == 0:
                    v['Location'] = self.sm.AddToDo(v)
                else:
                    v['Location'] = self.sm.SetToDo(v)

                # reread entry (it doesn't have to contain exactly same data as entered, it depends on phone features)
                v = self.sm.GetToDo(v['Location'])
                Wammu.Utils.ParseTodo(v)
                # append new value to list
                self.values['todo']['  '].append(v)
            except gammu.GSMError, val:
                v = backup
                self.ShowError(val[0])

            self.ActivateView('todo', '  ')
            try:
                self.browser.ShowLocation(v['Location'])
            except KeyError:
                pass


    def OnEdit(self, evt): 
        if self.type[0] == 'contact':
            if self.type[1] == '  ':
                t = '__'
            else:
                t = self.type[1]
            v = self.values['contact'][t][evt.index]
            self.EditContact(v);
        elif self.type[0] == 'calendar':
            if self.type[1] == '  ':
                t = '__'
            else:
                t = self.type[1]
            v = self.values['calendar'][t][evt.index]
            self.EditCalendar(v);
        elif self.type[0] == 'todo':
            if self.type[1] == '  ':
                t = '__'
            else:
                t = self.type[1]
            v = self.values['todo'][t][evt.index]
            self.EditTodo(v);
        else: 
            print 'Edit not yet implemented!'
            print evt.index

    def OnReply(self, evt): 
        if self.type[0] == 'message':
            if self.type[1] == '  ':
                t = '__'
            else:
                t = self.type[1]
            self.ComposeMessage({'Number': self.values['message'][t][evt.index]['Number']})
        else: 
            print 'Reply not yet implemented!'
            print evt.index
            
    def OnDuplicate(self, evt): 
        if self.type[0] == 'contact':
            if self.type[1] == '  ':
                t = '__'
            else:
                t = self.type[1]
            v = copy.deepcopy(self.values['contact'][t][evt.index])
            v['Location'] = 0
            self.EditContact(v)
        elif self.type[0] == 'calendar':
            if self.type[1] == '  ':
                t = '__'
            else:
                t = self.type[1]
            v = copy.deepcopy(self.values['calendar'][t][evt.index])
            v['Location'] = 0
            self.EditCalendar(v)
        elif self.type[0] == 'todo':
            if self.type[1] == '  ':
                t = '__'
            else:
                t = self.type[1]
            v = copy.deepcopy(self.values['todo'][t][evt.index])
            v['Location'] = 0
            self.EditTodo(v)
        elif self.type[0] == 'message':
            if self.type[1] == '  ':
                t = '__'
            else:
                t = self.type[1]
            v = copy.deepcopy(self.values['message'][t][evt.index])
            self.ComposeMessage(v)
        else: 
            print 'Duplicate not yet implemented!'
            print evt.index

        
    def OnSend(self, evt): 
        if self.type[0] == 'message':
            if self.type[1] == '  ':
                t = '__'
            else:
                t = self.type[1]
            v = self.values[self.type[0]][t][evt.index]
            try:
                for loc in v['Location'].split(', '):
                    # FIXME: 0 folder is safe for AT, but I'm not sure with others
                    self.sm.SendSavedSMS(0, int(loc))
            except gammu.GSMError, val:
                self.ShowError(val[0])

            if t == '__':
                t = '  '
            self.ActivateView(self.type[0], t)

    def SelectBackupFile(self, type, save = True):
        wildcard = ''
        if not save:
            wildcard += _('All backup formats') + '|*.backup;*.lmb;*.vcf;*.ldif;*.vcs;*.ics|'
            
        wildcard +=  _('Gammu backup [all data]') + ' (*.backup)|*.backup|'

        if type in ['contact', '']:
            wildcard += _('Nokia backup [contacts]') + ' (*.lmb)|*.lmb|'
        if type in ['contact', '']:
            wildcard += _('vCard [contacts]') + ' (*.vcf)|*.vcf|'
        if type in ['contact', '']:
            wildcard += _('LDIF [concacts]') + ' (*.ldif)|*.ldif|'
        if type in ['todo', 'calendar', '']:
            wildcard += _('vCalendar [todo,calendar]') + ' (*.vcs)|*.vcs|'
        if type in ['todo', 'calendar', '']:
            wildcard += _('iCalendar [todo,calendar]') + ' (*.ics)|*.ics|'
        
        wildcard += _('All files') + ' (*.*)|*.*;*'
         
        if save:
            dlg = wx.FileDialog(self, "Save backup as...", os.getcwd(), "", wildcard, wx.SAVE|wx.OVERWRITE_PROMPT|wx.CHANGE_DIR)
        else:
            dlg = wx.FileDialog(self, "Import backup", os.getcwd(), "", wildcard, wx.OPEN|wx.CHANGE_DIR)
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            return path
        return None

    def Import(self, evt):
        filename = self.SelectBackupFile('', save = False)
        if filename == None:
            return
        try:
            backup = gammu.ReadBackup(filename)
        except gammu.GSMError, val:
            info = val[0]
            evt = Wammu.Events.ShowMessageEvent(
                message = _('Error while saving backup:\n%s\nIn:%s\nError code: %d') % (info['Text'], info['Where'], info['Code']),
                title = _('Error Occured'),
                type = wx.ICON_ERROR)
            wx.PostEvent(self, evt)
            return
        choices = []
        values = []
        if len(backup['PhonePhonebook']) > 0:
            values.append('PhonePhonebook')
            choices.append(_('%d phone concacts entries') % len(backup['PhonePhonebook']))
        if len(backup['SIMPhonebook']) > 0:
            values.append('SIMPhonebook')
            choices.append(_('%d SIM contacts entries') % len(backup['SIMPhonebook']))
        if len(backup['ToDo']) > 0:
            values.append('ToDo')
            choices.append(_('%d ToDo entries') % len(backup['ToDo']))
        if len(backup['Calendar']) > 0:
            values.append('Calendar')
            choices.append(_('%d Calendar entries') % len(backup['Calendar']))

        if len(values) == 0:
            wx.MessageDialog(self, 
                _('No importable data were found in file "%s"') % filename,
                _('No data to import'),
                wx.OK | wx.ICON_INFORMATION).ShowModal()
            return
           
        msg = ''
        if backup['Model'] != '':
            msg = '\n \n' + _('Backup saved from phone %s') % backup['Model']
            if backup['IMEI'] != '':
                msg += _(', serial number %s') % backup['IMEI']
        if backup['Creator'] != '':
            msg += '\n \n' + _('Backup was created by %s') % backup['Creator']
        if backup['DateTime'] != None:
            msg += '\n \n' + _('Backup saved on %s') % str(backup['DateTime'])

        dlg = wx.lib.dialogs.MultipleChoiceDialog(self, _('Following data was found in backup, select which of these do you want to be added into phone.') + msg, _('Select what to import'),
                                    choices,style = wx.CHOICEDLG_STYLE | wx.RESIZE_BORDER,
                                    size = (600, 200))
        if dlg.ShowModal() != wx.ID_OK:
            return

        list = dlg.GetValue()
        if len(list) == 0:
            return

        try:
            busy = wx.BusyInfo(_('Importing data...'))
            for i in list:
                type = values[i]
                if type == 'PhonePhonebook':
                    for v in backup['PhonePhonebook']:
                        v['Location'] = self.sm.AddMemory(v)
                        # reread entry (it doesn't have to contain exactly same data as entered, it depends on phone features)
                        v = self.sm.GetMemory(v['MemoryType'], v['Location'])
                        Wammu.Utils.ParseMemoryEntry(v)
                        # append new value to list
                        self.values['contact'][v['MemoryType']].append(v)
                    self.ActivateView('contact', 'ME')
                elif type == 'SIMPhonebook':
                    for v in backup['SIMPhonebook']:
                        v['Location'] = self.sm.AddMemory(v)
                        # reread entry (it doesn't have to contain exactly same data as entered, it depends on phone features)
                        v = self.sm.GetMemory(v['MemoryType'], v['Location'])
                        Wammu.Utils.ParseMemoryEntry(v)
                        # append new value to list
                        self.values['contact'][v['MemoryType']].append(v)
                    self.ActivateView('contact', 'SM')
                elif type == 'ToDo':
                    for v in backup['ToDo']:
                        v['Location'] = self.sm.AddToDo(v)
                        # reread entry (it doesn't have to contain exactly same data as entered, it depends on phone features)
                        v = self.sm.GetToDo(v['Location'])
                        Wammu.Utils.ParseTodo(v)
                        # append new value to list
                        self.values['todo']['  '].append(v)
                    self.ActivateView('todo', '  ')
                elif type == 'Calendar':
                    for v in backup['Calendar']:
                        v['Location'] = self.sm.AddCalendar(v)
                        # reread entry (it doesn't have to contain exactly same data as entered, it depends on phone features)
                        v = self.sm.GetCalendar(v['Location'])
                        Wammu.Utils.ParseCalendar(v)
                        # append new value to list
                        self.values['calendar']['  '].append(v)
                    self.ActivateView('calendar', '  ')
        except gammu.GSMError, val:
            self.ShowError(val[0])

        wx.MessageDialog(self, 
            _('Backup has been imported from file "%s"') % filename,
            _('Backup imported'),
            wx.OK | wx.ICON_INFORMATION).ShowModal()

    def Backup(self, evt):
        filename = self.SelectBackupFile('')
        if filename == None:
            return
        ext = os.path.splitext(filename)[1].lower()
        backup = {}
        backup['Creator'] = 'Wammu ' + Wammu.__version__
        backup['IMEI'] = self.IMEI
        backup['Model'] = '%s %s %s' % ( self.Manufacturer, self.Model, self.Version)
        if ext in ['.vcf', '.ldif']:
            # these support only one phonebook, so merged it
            backup['PhoneBackup'] = self.values['contact']['ME'] + self.values['contact']['SM']
        else:
            backup['PhonePhonebook'] = self.values['contact']['ME']
            backup['SIMPhonebook'] = self.values['contact']['SM']

        backup['ToDo'] = self.values['todo']['  ']
        backup['Calendar'] = self.values['calendar']['  ']

        try:
            gammu.SaveBackup(filename, backup)
            wx.MessageDialog(self, 
                _('Backup has been saved to file "%s"') % filename,
                _('Backup saved'),
                wx.OK | wx.ICON_INFORMATION).ShowModal()
        except gammu.GSMError, val:
            info = val[0]
            evt = Wammu.Events.ShowMessageEvent(
                message = _('Error while saving backup:\n%s\nIn:%s\nError code: %d') % (info['Text'], info['Where'], info['Code']),
                title = _('Error Occured'),
                type = wx.ICON_ERROR)
            wx.PostEvent(self, evt)
    
    def OnBackup(self, evt):
        filename = self.SelectBackupFile(self.type[0])
        if filename == None:
            return
        ext = os.path.splitext(filename)[1].lower()
        if self.type[1] == '  ':
            t = '__'
        else:
            t = self.type[1]
        lst = []
        for i in evt.list:
            lst.append(self.values[self.type[0]][t][i])
        backup = {}
        backup['Creator'] = 'Wammu ' + Wammu.__version__
        backup['IMEI'] = self.IMEI
        backup['Model'] = '%s %s %s' % ( self.Manufacturer, self.Model, self.Version)
        if self.type[0] == 'contact':
            if ext in ['.vcf', '.ldif']:
                # these support only one phonebook, so keep it merged
                backup['PhoneBackup'] = lst
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

        try:
            gammu.SaveBackup(filename, backup)
            wx.MessageDialog(self, 
                _('Backup has been saved to file "%s"') % filename,
                _('Backup saved'),
                wx.OK | wx.ICON_INFORMATION).ShowModal()
        except gammu.GSMError, val:
            info = val[0]
            evt = Wammu.Events.ShowMessageEvent(
                message = _('Error while saving backup:\n%s\nIn:%s\nError code: %d') % (info['Text'], info['Where'], info['Code']),
                title = _('Error Occured'),
                type = wx.ICON_ERROR)
            wx.PostEvent(self, evt)
    
    def OnDelete(self, evt):
        # FIXME: add here confirmation?
        if self.type[0] == 'contact' or self.type[0] == 'call':
            if self.type[1] == '  ':
                t = '__'
            else:
                t = self.type[1]
            try:
                busy = wx.BusyInfo(_('Deleting contact...'))
                lst = []
                for i in evt.list:
                    lst.append(self.values[self.type[0]][t][i])
                for v in lst:
                    self.sm.DeleteMemory(v['MemoryType'], v['Location'])
                    for idx in range(len(self.values[self.type[0]][v['MemoryType']])):
                        if self.values[self.type[0]][v['MemoryType']][idx] == v:
                            del self.values[self.type[0]][v['MemoryType']][idx]
                            break
            except gammu.GSMError, val:
                self.ShowError(val[0])

            if t == '__':
                t = '  '
            self.ActivateView(self.type[0], t)
        elif self.type[0] == 'message':
            if self.type[1] == '  ':
                t = '__'
            else:
                t = self.type[1]
            try:
                busy = wx.BusyInfo(_('Deleting message...'))
                lst = []
                for i in evt.list:
                    lst.append(self.values[self.type[0]][t][i])
                for v in lst:
                    for loc in v['Location'].split(', '):
                        self.sm.DeleteSMS(v['Folder'], int(loc))
                    for idx in range(len(self.values[self.type[0]][v['State']])):
                        if self.values[self.type[0]][v['State']][idx] == v:
                            del self.values[self.type[0]][v['State']][idx]
                            break
            except gammu.GSMError, val:
                self.ShowError(val[0])

            if t == '__':
                t = '  '
            self.ActivateView(self.type[0], t)
        elif self.type[0] == 'todo':
            if self.type[1] == '  ':
                t = '__'
            else:
                t = self.type[1]
            try:
                busy = wx.BusyInfo(_('Deleting todo...'))
                lst = []
                for i in evt.list:
                    lst.append(self.values[self.type[0]][t][i])
                for v in lst:
                    self.sm.DeleteToDo(v['Location'])
                    for idx in range(len(self.values[self.type[0]]['  '])):
                        if self.values[self.type[0]]['  '][idx] == v:
                            del self.values[self.type[0]]['  '][idx]
                            break
            except gammu.GSMError, val:
                self.ShowError(val[0])

            if t == '__':
                t = '  '
            self.ActivateView(self.type[0], t)
        elif self.type[0] == 'calendar':
            if self.type[1] == '  ':
                t = '__'
            else:
                t = self.type[1]
            try:
                busy = wx.BusyInfo(_('Deleting calendar event...'))
                lst = []
                for i in evt.list:
                    lst.append(self.values[self.type[0]][t][i])
                for v in lst:
                    self.sm.DeleteCalendar(v['Location'])
                    for idx in range(len(self.values[self.type[0]]['  '])):
                        if self.values[self.type[0]]['  '][idx] == v:
                            del self.values[self.type[0]]['  '][idx]
                            break
            except gammu.GSMError, val:
                self.ShowError(val[0])

            if t == '__':
                t = '  '
            self.ActivateView(self.type[0], t)
        else: 
            print 'Delete not yet implemented! (items to delete = %s)' % str(evt.list)

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

    def OnProgress(self, evt): 
        if not self.progress.Update(evt.progress):
            try:
                evt.cancel()
            except:
                pass
        if (evt.progress == 100):
            self.progress.Destroy()
        if hasattr(evt, 'lock'):
            evt.lock.release()

    def OnShowMessage(self, evt): 
        try:
            if self.progress.IsShown():
                parent = self.progress
            else:
                parent = self
        except:
            parent = self

        dlg = wx.MessageDialog(self, 
            StrConv(evt.message),
            StrConv(evt.title),
            wx.OK | evt.type).ShowModal()
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
    # Time
    #

    def SyncTime(self, event):
        busy = wx.BusyInfo(_('Setting time in phone...'))
        try:
            self.sm.SetDateTime(datetime.datetime.now())
        except gammu.GSMError, val:
            del busy
            self.ShowError(val[0])
    
    #
    # Connecting / Disconnecting
    #

    def PhoneConnect(self, event = None):
        busy = wx.BusyInfo(_('One moment please, connecting to phone...'))
        cfg = {
            'StartInfo': self.cfg.Read('/Gammu/StartInfo', 'no'), 
            'UseGlobalDebugFile': 1, 
            'DebugFile': None, # Set on other place
            'SyncTime': self.cfg.Read('/Gammu/SyncTime', 'no'), 
            'Connection': self.cfg.Read('/Gammu/Connection', Wammu.Connections[0]), 
            'LockDevice': self.cfg.Read('/Gammu/LockDevice', 'no'), 
            'DebugLevel': 'textall', # Set on other place
            'Device': self.cfg.Read('/Gammu/Device', Wammu.Devices[0]), 
            'Localize': None,  # Set automatically by python-gammu
            'Model': self.cfg.Read('/Gammu/Model', Wammu.Models[0])
            }
        self.sm.SetConfig(0, cfg)
        try:
            self.sm.Init()
            self.TogglePhoneMenus(True)
            try:
                self.IMEI = self.sm.GetIMEI()
            except:
                self.IMEI = ''
            try:
                self.Manufacturer = self.sm.GetManufacturer()
            except:
                self.Manufacturer = ''
            try:
                m = self.sm.GetModel()
                if m[0] == '':
                    self.Model = m[1]
                else:
                    self.Model = m[0]
            except:
                self.Model = ''
            try:
                self.Version = self.sm.GetFirmware()[0]
            except:
                self.Version = ''
              
        except gammu.GSMError, val:
            del busy
            self.ShowError(val[0])
            try:
                self.sm.Terminate()
            except gammu.GSMError, val:
                pass
        
    def PhoneDisconnect(self, event = None):
        busy = wx.BusyInfo(_('One moment please, disconnecting from phone...'))
        try:
            self.sm.Terminate()
        except gammu.ERR_NOTCONNECTED:
            pass
        except gammu.GSMError, val:
            del busy
            self.ShowError(val[0])
        self.TogglePhoneMenus(False)

    def SearchMessage(self, text):
        evt = Wammu.Events.TextEvent(text = text + '\n')
        wx.PostEvent(self.searchlog, evt)
    
    def SearchDone(self, list):
        self.founddevices = list
        evt = Wammu.Events.DoneEvent()
        wx.PostEvent(self.searchlog, evt)
  
    def SearchPhone(self, evt = None):
        self.founddevices = []
        self.PhoneDisconnect()
        d = Wammu.PhoneSearch.LogDialog(self)
        self.searchlog = d
        t = Wammu.PhoneSearch.AllSearchThread(lock = self.cfg.Read('/Gammu/LockDevice', 'no'), callback = self.SearchDone, msgcallback = self.SearchMessage)
        t.start()
        d.ShowModal()

        if len(self.founddevices) == 0:
            wx.MessageDialog(self,
                _('No phone could not be found, you still can try to select it manually. Wammu searches only few ports, so if you are using some unusual, this might easilly happen.'),
                _('No phone found'),
                wx.OK | wx.ICON_WARNING).ShowModal()
            return
            
        choices = []
        for x in self.founddevices:
            choices.append(_('Model %s (%s) on %s port using connection %s') % (x[2][1], x[3], x[0], x[1]))
        dlg = wx.SingleChoiceDialog(self, _('Select phone to use from bellow list'), _('Select phone'),
                                    choices, wx.CHOICEDLG_STYLE | wx.RESIZE_BORDER)
        if dlg.ShowModal() == wx.ID_OK:
            idx = dlg.GetSelection()
            x = self.founddevices[idx]
            self.cfg.Write('/Gammu/Model', '')
            self.cfg.Write('/Gammu/Device', x[0])
            self.cfg.Write('/Gammu/Connection', x[1])

    def About(self, evt = None):
        Wammu.About.AboutBox(self).ShowModal()
