# Wammu - Phone manager
# Copyright (c) 2003-4 Michal Cihar 
#
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 2 of the License, or (at your option)
# any later version.
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
Items browser
'''

import wx
import Wammu
import Wammu.Events
import Wammu.Utils
import gammu
import sys
import traceback
from Wammu.Paths import *
from Wammu.Utils import StrConv, Str_ as _

import wx.lib.mixins.listctrl 

class Browser(wx.ListCtrl, wx.lib.mixins.listctrl.ListCtrlAutoWidthMixin):
    def __init__(self, parent, win):
        wx.ListCtrl.__init__(self, parent, -1,
                            style=wx.LC_REPORT|wx.LC_VIRTUAL|wx.LC_HRULES|wx.LC_VRULES)
        self.win = win

        self.itemno = -1

        self.attr1 = wx.ListItemAttr()

        self.attr2 = wx.ListItemAttr()
        self.attr2.SetBackgroundColour('light blue')

        il = wx.ImageList(16, 16)
        self.downarrow = il.Add(wx.Bitmap(MiscPath('downarrow')))
        self.uparrow = il.Add(wx.Bitmap(MiscPath('uparrow')))
        self.AssignImageList(il, wx.IMAGE_LIST_SMALL)

        wx.EVT_LIST_ITEM_SELECTED(self, self.GetId(), self.OnItemSelected)
        wx.EVT_LIST_ITEM_ACTIVATED(self, self.GetId(), self.OnItemActivated)
        wx.EVT_LIST_KEY_DOWN(self, self.GetId(), self.OnKey)
        wx.EVT_LIST_COL_CLICK(self, self.GetId(), self.OnColClick)
        wx.EVT_LIST_ITEM_RIGHT_CLICK(self, self.GetId(), self.OnRightClick)
        wx.lib.mixins.listctrl.ListCtrlAutoWidthMixin.__init__(self)

    def ShowHeaders(self):
        if self.type == 'info':
            self.columns = (_('Name'), _('Value'))
            self.keys = (0, 1)
        elif self.type == 'contact':
            self.columns = ( _('Location'), _('Memory'), _('Name'), _('Number'))
            self.keys = ('Location', 'MemoryType', 'Name', 'Number')
        elif self.type == 'call':
            self.columns = ( _('Location'), _('Type'), _('Name'), _('Number'))
            self.keys = ('Location', 'MemoryType', 'Name', 'Number')
        elif self.type == 'message':
            self.columns = ( _('Location'), _('State'), _('Number'), _('Date'), _('Text'))
            self.keys = ('Location', 'State', 'Number', 'DateTime', 'Text')
        elif self.type == 'todo':
            self.columns = ( _('Location'), _('Completed'), _('Priority'), _('Text'), _('Date'))
            self.keys = ('Location', 'Completed', 'Priority', 'Text', 'Date')
        elif self.type == 'calendar':
            self.columns = ( _('Location'), _('Start'), _('End'), _('Text'))
            self.keys = ('Location', 'Start', 'End', 'Text')

        cnt = len(self.columns)
        
        for i in range(cnt):
            self.InsertColumn(i, self.columns[i])

        # resize columns to fit content
        
        # FIXME: this should be acquired better!
        spc = 10
        
        max = [0] * cnt
        for i in range(cnt):
            size = self.GetTextExtent(StrConv(self.columns[i]))[0]
            # 16 bellow is for sort arrrow
            if (size + 16 > max[i]):
                max[i] = size + 16
            
        for x in self.values:
            for i in range(cnt):
                size = self.GetTextExtent(StrConv(x[self.keys[i]]))
                if (size[0] > max[i]):
                    max[i] = size[0]
        for i in range(cnt - 1):
            self.SetColumnWidth(i, max[i] + spc)
        self.resizeLastColumn(max[cnt - 1] + spc)
    
    def Sorter(self, i1, i2):
        if self.sortkey == 'Location' and type(i1[self.sortkey]) == type(''):
            return self.sortorder * cmp(int(i1[self.sortkey].split(', ')[0]), int(i2[self.sortkey].split(', ')[0]))
        return self.sortorder * cmp(i1[self.sortkey], i2[self.sortkey])

    def ShowLocation(self, loc, second = None):
        result = Wammu.Utils.SearchLocation(self.values, loc, second)
        if result != -1:
            self.ShowRow(result)
    
    def ShowRow(self, id):
        if self.GetItemCount() > id and id >= 0:
            self.itemno = id
            index = self.GetFirstSelected()
            while index != -1:
                self.SetItemState(index, 0, wx.LIST_STATE_SELECTED)
                index = self.GetFirstSelected()

            self.SetItemState(id, wx.LIST_STATE_FOCUSED | wx.LIST_STATE_SELECTED, wx.LIST_STATE_FOCUSED | wx.LIST_STATE_SELECTED)
            self.EnsureVisible(id)
        else:
            evt = Wammu.Events.ShowEvent(index = None)
            wx.PostEvent(self.win, evt)
        
    def Change(self, type, values):
        self.type = type
        self.values = values
        self.sortkey = ''
        self.ClearAll()
        self.SetItemCount(len(values))
        self.ShowHeaders()
        self.Resort(0)

    def Resort(self, col):
        # remember show item
        try:
            item = self.values[self.itemno]
        except IndexError:
            item = None
        # find keys and order
        nextsort = self.keys[col]
        if nextsort == self.sortkey:
            self.sortorder = -1 * self.sortorder
        else:
            self.sortorder = 1
        self.sortkey = nextsort

        # do the real sort
        self.values.sort(self.Sorter)

        # set image
        for i in range(self.GetColumnCount()):
            self.ClearColumnImage(i)
        if self.sortorder == 1:
            image = self.downarrow
        else:
            image = self.uparrow
        self.SetColumnImage(col, image)

        # refresh displayed items
        if self.GetItemCount() != 0:
            top = self.GetTopItem() 
            if top < 0:
                top = 0
            count = self.GetCountPerPage()
            totalcount = self.GetItemCount()
            if count < 0:
                count = totalcount
            last = min(totalcount - 1, top + count)
            self.RefreshItems(top, last)
            
            if item != None:
                self.ShowRow(self.values.index(item))

    def OnKey(self, evt):
        if evt.GetKeyCode() == wx.WXK_DELETE:
            self.DoSelectedDelete()
  
    def DoSelectedDelete(self):
        list = []
        index = self.GetFirstSelected()
        while index != -1:
            list.append(index)
            index = self.GetNextSelected(index)
        self.DoDelete(list)
  
    def DoDelete(self, list):
        evt = Wammu.Events.DeleteEvent(list = list)
        wx.PostEvent(self.win, evt)
        
    def DoBackup(self, list):
        evt = Wammu.Events.BackupEvent(list = list)
        wx.PostEvent(self.win, evt)
        
    def OnRightClick(self, evt):
        if self.type == 'info':
            return
        self.popupIndex = evt.m_itemIndex
        # only do this part the first time so the events are only bound once
        if not hasattr(self, "popupIDEdit"):
            self.popupIDSend        = wx.NewId()
            self.popupIDEdit        = wx.NewId()
            self.popupIDMessage     = wx.NewId()
            self.popupIDCall        = wx.NewId()
            self.popupIDDelete      = wx.NewId()
            self.popupIDDeleteSel   = wx.NewId()
            self.popupIDDuplicate   = wx.NewId()
            self.popupIDReply       = wx.NewId()
            self.popupIDBackupOne   = wx.NewId()
            self.popupIDBackupSel   = wx.NewId()
            self.popupIDBackupAll   = wx.NewId()

            wx.EVT_MENU(self, self.popupIDSend,         self.OnPopupSend)
            wx.EVT_MENU(self, self.popupIDEdit,         self.OnPopupEdit)
            wx.EVT_MENU(self, self.popupIDMessage,      self.OnPopupMessage)
            wx.EVT_MENU(self, self.popupIDCall,         self.OnPopupCall)
            wx.EVT_MENU(self, self.popupIDDelete,       self.OnPopupDelete)
            wx.EVT_MENU(self, self.popupIDDeleteSel,    self.OnPopupDeleteSel)
            wx.EVT_MENU(self, self.popupIDDuplicate,    self.OnPopupDuplicate)
            wx.EVT_MENU(self, self.popupIDReply,        self.OnPopupReply)
            wx.EVT_MENU(self, self.popupIDBackupOne,    self.OnPopupBackupOne)
            wx.EVT_MENU(self, self.popupIDBackupSel,    self.OnPopupBackupSel)
            wx.EVT_MENU(self, self.popupIDBackupAll,    self.OnPopupBackupAll)

        # make a menu
        menu = wx.Menu()
        # add some items
        if self.type == 'message':
            if self.values[evt.m_itemIndex]['State'] == 'Sent':
                menu.Append(self.popupIDSend,       _('Resend'))
            if self.values[evt.m_itemIndex]['State'] == 'UnSent':
                menu.Append(self.popupIDSend,       _('Send'))
            if self.values[evt.m_itemIndex]['State'] == 'Read' or self.values[evt.m_itemIndex]['State'] == 'UnRead':
                menu.Append(self.popupIDReply,      _('Reply'))
            if self.values[evt.m_itemIndex]['Number'] != '':
                menu.Append(self.popupIDCall,       _('Call'))
            menu.AppendSeparator()
            
        if self.type in ['contact', 'call']:
            menu.Append(self.popupIDMessage,    _('Send message'))
            menu.Append(self.popupIDCall,       _('Call'))
            menu.AppendSeparator()
            
        if not self.type in ['call', 'message']:
            menu.Append(self.popupIDEdit,       _('Edit'))
        if not self.type in ['call']:
            menu.Append(self.popupIDDuplicate,  _('Duplicate'))
            menu.AppendSeparator()

        menu.Append(self.popupIDDelete,     _('Delete current'))
        menu.Append(self.popupIDDeleteSel,  _('Delete selected'))

        if self.type != 'message':
            menu.AppendSeparator()
            menu.Append(self.popupIDBackupOne,  _('Backup current'))
            menu.Append(self.popupIDBackupSel,  _('Backup selected'))
            menu.Append(self.popupIDBackupAll,  _('Backup all'))

        # Popup the menu.  If an item is selected then its handler
        # will be called before PopupMenu returns.
        self.PopupMenu(menu, evt.GetPoint())
        menu.Destroy()
    
    def OnPopupDuplicate(self, event):
        evt = Wammu.Events.DuplicateEvent(index = self.popupIndex)
        wx.PostEvent(self.win, evt)

    def OnPopupReply(self, event):
        evt = Wammu.Events.ReplyEvent(index = self.popupIndex)
        wx.PostEvent(self.win, evt)

    def OnPopupSend(self, event):
        evt = Wammu.Events.SendEvent(index = self.popupIndex)
        wx.PostEvent(self.win, evt)

    def OnPopupCall(self, event):
        evt = Wammu.Events.CallEvent(index = self.popupIndex)
        wx.PostEvent(self.win, evt)

    def OnPopupMessage(self, event):
        evt = Wammu.Events.MessageEvent(index = self.popupIndex)
        wx.PostEvent(self.win, evt)

    def OnPopupEdit(self, event):
        evt = Wammu.Events.EditEvent(index = self.popupIndex)
        wx.PostEvent(self.win, evt)

    def OnPopupDelete(self, event):
        self.DoDelete([self.popupIndex])

    def OnPopupDeleteSel(self, event):
        self.DoSelectedDelete()

    def OnPopupBackupOne(self, event):
        self.DoBackup([self.popupIndex])

    def OnPopupBackupSel(self, event):
        list = []
        index = self.GetFirstSelected()
        while index != -1:
            list.append(index)
            index = self.GetNextSelected(index)
        self.DoBackup(list)

    def OnPopupBackupAll(self, event):
        self.DoBackup(range(self.GetItemCount()))

    def OnColClick(self, evt):
        self.Resort(evt.GetColumn())
        
    def OnItemSelected(self, event):
        self.itemno = event.m_itemIndex
        evt = Wammu.Events.ShowEvent(index = event.m_itemIndex)
        wx.PostEvent(self.win, evt)

    def OnItemActivated(self, event):
        evt = Wammu.Events.EditEvent(index = event.m_itemIndex)
        wx.PostEvent(self.win, evt)

    def getColumnText(self, index, col):
        item = self.GetItem(index, col)
        return item.GetText()



    def OnGetItemText(self, item, col):
        return StrConv(self.values[item][self.keys[col]])

    def OnGetItemAttr(self, item):
        if item % 2 == 1:
            return self.attr1
        else:
            return self.attr2


