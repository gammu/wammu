import wx
import wx.html
import gammu
import sys
import datetime
import Wammu

import Wammu.Info
import Wammu.Memory

import Wammu.Events
import Wammu.Displayer
import Wammu.Browser
from Wammu.Paths import *
import threading

## Create a new frame class, derived from the wxPython Frame.
class WammuFrame(wx.Frame):

    def __init__(self, parent, id):
        wx.Frame.__init__(self, parent, id, 'Wammu', wx.DefaultPosition, wx.Size(640,480), wx.DEFAULT_FRAME_STYLE)
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

        self.splitter = wx.SplitterWindow(self, -1)
        il = wx.ImageList(16, 16)

        self.tree = wx.TreeCtrl(self.splitter)
        self.tree.AssignImageList(il)

        self.treei = {}
        self.treei['info'] = {}
        self.treei['call'] = {}
        self.treei['memory'] = {}

        # Fill tree
        self.treei['info']['  '] = self.tree.AddRoot('Phone', il.Add(wx.Bitmap(IconPath('phone'))))

        # calls
        self.treei['call']['  '] = self.tree.AppendItem(self.treei['info']['  '], 'Calls', il.Add(wx.Bitmap(IconPath('call'))))
        self.treei['call']['RC'] = self.tree.AppendItem(self.treei['call']['  '], 'Received', il.Add(wx.Bitmap(IconPath('call-received'))))
        self.treei['call']['MC'] = self.tree.AppendItem(self.treei['call']['  '], 'Missed', il.Add(wx.Bitmap(IconPath('call-missed'))))
        self.treei['call']['DC'] = self.tree.AppendItem(self.treei['call']['  '], 'Outgoing', il.Add(wx.Bitmap(IconPath('call-outgoing'))))

        
        # contacts
        self.treei['memory']['  '] = self.tree.AppendItem(self.treei['info']['  '], 'Contact', il.Add(wx.Bitmap(IconPath('contact'))))
        self.treei['memory']['SM'] = self.tree.AppendItem(self.treei['memory']['  '], 'SIM', il.Add(wx.Bitmap(IconPath('contact-sim'))))
        self.treei['memory']['ME'] = self.tree.AppendItem(self.treei['memory']['  '], 'Phone', il.Add(wx.Bitmap(IconPath('contact-phone'))))

        self.tree.Expand(self.treei['info']['  '])
        self.tree.Expand(self.treei['call']['  '])
        self.tree.Expand(self.treei['memory']['  '])
        
        wx.EVT_TREE_SEL_CHANGED(self, self.tree.GetId(), self.OnTreeSel)
        

        # right frame
        self.rightsplitter = wx.SplitterWindow(self.splitter, -1)
        self.rightwin = wx.Panel(self.rightsplitter, -1)
        self.rightwin.sizer = wx.BoxSizer(wx.VERTICAL)
        
        # title text
        self.label = wx.StaticText(self.rightwin, -1, 'Wammu')
        self.rightwin.sizer.Add(self.label, 0, wx.LEFT|wx.ALL, 2)

        # line
        self.rightwin.sizer.Add(wx.StaticLine(self.rightwin, -1), 0 , wx.EXPAND)

        # item browser
        self.browser = Wammu.Browser.Browser(self.rightwin, self)
        self.rightwin.sizer.Add(self.browser, 1, wx.EXPAND)
        self.rightwin.SetSizer(self.rightwin.sizer)

        # values displayer
        self.content = Wammu.Displayer.Displayer(self.rightsplitter, self)
        self.rightsplitter.SplitHorizontally(self.rightwin, self.content, -200)

        self.splitter.SplitVertically(self.tree, self.rightsplitter, 160)

        # initial content
        self.content.SetPage('<body><html><font size=+1><b>Welcome to Wammu ' + Wammu.__version__ + '</b></font><br><a href="memory://ME/1">Mem 1</a></html></body>')

        # Prepare the menu bar
        self.menuBar = wx.MenuBar()

        # 1st menu from left
        menu1 = wx.Menu()
        menu1.Append(101, '&SearchPhone', 'Search for phone')
        menu1.AppendSeparator()
        menu1.Append(150, '&Settings', 'Change Wammu settings')
        menu1.AppendSeparator()
        menu1.Append(199, 'E&xit', 'Exit Wammu')
        # Add menu to the menu bar
        self.menuBar.Append(menu1, '&Wammu')
        
        # 2st menu from left
        menu2 = wx.Menu()
        menu2.Append(201, '&Connect', 'Connect the device')
        menu2.Append(202, '&Disconnect', 'Disconnect the device')
        menu2.AppendSeparator()
        menu2.Append(210, '&Synchronise time', 'Synchronises time in mobile with PC')
        # Add menu to the menu bar
        self.menuBar.Append(menu2, '&Phone')

        # 2st menu from left
        menu3 = wx.Menu()
        menu3.Append(301, '&Info', 'Get phone information')
        menu3.AppendSeparator()
        menu3.Append(310, 'Contacts (&SIM)', 'Contacts from SIM')
        menu3.Append(311, 'Contacts (&phone)', 'Contacts from phone memory')
        menu3.Append(312, '&Contacts (All)', 'Contacts from phone and SIM memory')
        menu3.AppendSeparator()
        menu3.Append(320, 'C&alls', 'Calls')
        # Add menu to the menu bar
        self.menuBar.Append(menu3, '&Retrieve')

        # Set menu bar
        self.SetMenuBar(self.menuBar)

        # some menu events
        wx.EVT_MENU(self, 199, self.CloseWindow)
        
        wx.EVT_MENU(self, 201, self.PhoneConnect)
        wx.EVT_MENU(self, 202, self.PhoneDisconnect)
        wx.EVT_MENU(self, 210, self.SyncTime)

        wx.EVT_MENU(self, 301, self.ShowInfo)
        wx.EVT_MENU(self, 310, self.ShowContactsSM)
        wx.EVT_MENU(self, 311, self.ShowContactsME)
        wx.EVT_MENU(self, 312, self.ShowContacts)
        wx.EVT_MENU(self, 320, self.ShowCalls)


        self.TogglePhoneMenus(False)

        self.values = {}
        self.values['info'] = {}
        self.values['memory'] = {}
        self.values['call'] = {}
        
        self.values['info']['  '] = [['Wammu version', Wammu.__version__], ['Gammu version', gammu.Version()]]
        self.values['memory']['  '] = []
        self.values['memory']['SM'] = []
        self.values['memory']['ME'] = []
        self.values['call']['  '] = []
        self.values['call']['RC'] = []
        self.values['call']['MC'] = []
        self.values['call']['DC'] = []
        
        self.type = ['info','  ']
        self.ChangeBrowser('info', '  ')

        # create state machine
        self.sm = gammu.StateMachine()
        # read configuration, FIXME: this should be done from GUI
        self.sm.ReadConfig()

    def TogglePhoneMenus(self, enable):
        if enable:
            self.SetStatusText('Connected', 1)
        else:
            self.SetStatusText('Disconnected', 1)
        mb = self.menuBar

        mb.Enable(201, not enable);
        mb.Enable(202, enable);
        
        mb.Enable(210, enable);

        mb.Enable(301, enable);

        mb.Enable(310, enable);
        mb.Enable(311, enable);
        mb.Enable(312, enable);
        
        mb.Enable(320, enable);

    def ActivateView(self, k1, k2):
        self.tree.SelectItem(self.treei[k1][k2])
        self.ChangeBrowser(k1, k2)

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

    def OnTreeSel(self, event):
        item = event.GetItem()
        for k1, v1 in self.treei.iteritems():
            for k2, v2 in v1.iteritems():
                if v2 == item:
                    self.ChangeBrowser(k1, k2)

    def CloseWindow(self, event):
        # tell the window to kill itself
        self.Destroy()

    def ShowError(self, info):
        evt = Wammu.Events.ShowMessageEvent(
            message = 'Got error from phone:\n%s\nIn:%s\nError code: %d' % (info['Text'], info['Where'], info['Code']),
            title = 'Error Occured',
            type = wx.ICON_ERROR)
        wx.PostEvent(self, evt)

    def ShowProgress(self, text):
        self.progress = wx.ProgressDialog(text,
                       'Operation in progress',
                       100,
                       self,
                       wx.PD_CAN_ABORT | wx.PD_APP_MODAL | wx.PD_AUTO_HIDE | wx.PD_ELAPSED_TIME | wx.PD_REMAINING_TIME | wx.PD_ESTIMATED_TIME)

    def OnData(self, evt):
        self.values[evt.type[0]][evt.type[1]] = evt.data
        if hasattr(self, 'nextfun'):
            f = self.nextfun
            a = self.nextarg
            del self.nextfun
            del self.nextarg
            f (*a)
            
    def OnShow(self, evt): 
        if self.type == ['info','  ']:
            self.content.SetPage('<body><html><b>' + self.values['info']['__'][evt.index][0] + '</b>: ' + self.values['info']['__'][evt.index][1] + '</html></body>')
        elif self.type[0] == 'memory' or self.type[0] == 'call' :
            text = ''
            if self.type[1] == '  ':
                t = '__'
            else:
                t = self.type[1]
            v = self.values[self.type[0]][t][evt.index]
            text =  text + '<tr><td><b>Location:</b></td><td>' + str(v['Location']) + '</td></tr>'
            text =  text + '<tr><td><b>Memory type:</b></td><td>' + v['MemoryType'] + '</td></tr>'
            for i in v['Values']:
                text = text + '<tr><td><b>' + i['Type'] + ':</b></td><td>' + str(i['Value']) + '</td></tr>'
            self.content.SetPage('<body><html><table border=1>' + text + '</table></html></body>')
        else:
            print 'Show not yet implemented!'
            print evt.index

    def OnEdit(self, evt): 
        print 'Edit not yet implemented!'
        print evt.index

    def OnLink(self, evt): 
        print 'Links not yet implemented!'
        print evt.link

    def OnProgress(self, evt): 
        if not self.progress.Update(evt.progress):
            try:
                evt.cancel()
            except:
                pass
        if (evt.progress == 100):
            self.progress.Destroy()
        try:
            evt.lock.release()
        except AttributeError:
            pass

    def OnShowMessage(self, evt): 
        try:
            if self.progress.IsShown():
                parent = self.progress
            else:
                parent = self
        except:
            parent = self

        dlg = wx.MessageDialog(self, 
            evt.message,
            evt.title,
            wx.OK | evt.type)
        dlg.ShowModal()
        dlg.Destroy()
        try:
            evt.lock.release()
        except AttributeError:
            pass

    def ShowInfo(self, event):
        self.ShowProgress('Reading phone information')
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
        self.ShowProgress('Reading calls of type ' + type)
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
        self.nextarg = ('memory', '  ')

    def ShowContactsME(self, event):
        self.GetContactsType('ME')
        self.nextfun = self.ActivateView
        self.nextarg = ('memory', 'ME')
        
    def ShowContactsSM(self, event):
        self.GetContactsType('SM')
        self.nextfun = self.ActivateView
        self.nextarg = ('memory', 'SM')
        
    def GetContactsType(self, type):
        self.ShowProgress('Reading contacts from ' + type)
        Wammu.Memory.GetMemory(self, self.sm, 'memory', type).start()

    #
    # Time
    #

    def SyncTime(self, event):
        busy = wx.BusyInfo('Setting time in phone...')
        try:
            self.sm.SetDateTime(datetime.datetime.now())
        except gammu.GSMError, val:
            self.ShowError(val[0])
    
    #
    # Connecting / Disconneting
    #

    def PhoneConnect(self, event):
        busy = wx.BusyInfo('One moment please, connecting to phone...')
        try:
            self.sm.Init()
            self.TogglePhoneMenus(True)
        except gammu.GSMError, val:
            self.ShowError(val[0])
            try:
                self.sm.Terminate()
            except gammu.GSMError, val:
                pass
        
    def PhoneDisconnect(self, event):
        busy = wx.BusyInfo('One moment please, disconnecting to phone...')
        try:
            self.sm.Terminate()
        except gammu.GSMError, val:
            self.ShowError(val[0])
        self.TogglePhoneMenus(False)

