import wx
import Wammu
import Wammu.Events
import Wammu.Utils
import gammu

import wx.lib.mixins.listctrl 

class Browser(wx.ListCtrl, wx.lib.mixins.listctrl.ListCtrlAutoWidthMixin):
    def __init__(self, parent, win):
        wx.ListCtrl.__init__(self, parent, -1,
                            style=wx.LC_REPORT|wx.LC_VIRTUAL|wx.LC_HRULES|wx.LC_VRULES)
        self.win = win

        self.attr1 = wx.ListItemAttr()

        self.attr2 = wx.ListItemAttr()
        self.attr2.SetBackgroundColour('light blue')

        wx.EVT_LIST_ITEM_SELECTED(self, self.GetId(), self.OnItemSelected)
        wx.EVT_LIST_ITEM_ACTIVATED(self, self.GetId(), self.OnItemActivated)
##        wx.lib.mixins.listctrl.ColumnSorterMixin
        wx.lib.mixins.listctrl.ListCtrlAutoWidthMixin.__init__(self)

    def ShowHeaders(self):
        if self.type == 'info':
            self.InsertColumn(0, 'Name')
            self.InsertColumn(1, 'Value')
#            self.SetColumnWidth(0, 100)
#            self.SetColumnWidth(1, 200)
            self.SetColumnWidth(0, wx.LIST_AUTOSIZE)
#            self.SetColumnWidth(1, wx.LIST_AUTOSIZE)
        elif self.type == 'memory':
            self.InsertColumn(0, 'Location')
            self.InsertColumn(1, 'Memory')
            self.InsertColumn(2, 'Name')
            self.InsertColumn(3, 'Number')
            self.SetColumnWidth(0, wx.LIST_AUTOSIZE)
            self.SetColumnWidth(1, wx.LIST_AUTOSIZE)
            self.SetColumnWidth(2, wx.LIST_AUTOSIZE)
            self.SetColumnWidth(3, wx.LIST_AUTOSIZE)
        elif self.type == 'call':
            self.InsertColumn(0, 'Location')
            self.InsertColumn(1, 'Type')
            self.InsertColumn(2, 'Name')
            self.InsertColumn(3, 'Number')
            self.SetColumnWidth(0, wx.LIST_AUTOSIZE)
            self.SetColumnWidth(1, wx.LIST_AUTOSIZE)
            self.SetColumnWidth(2, wx.LIST_AUTOSIZE)
            self.SetColumnWidth(3, wx.LIST_AUTOSIZE)
        self.resizeLastColumn(0)
    
    def Change(self, type, values):
        self.type = type
        self.values = values
        self.ClearAll()
        self.SetItemCount(len(self.values))
        self.ShowHeaders()

    def OnItemSelected(self, event):
        evt = Wammu.Events.ShowEvent(index = event.m_itemIndex)
        wx.PostEvent(self.win, evt)

    def OnItemActivated(self, event):
        evt = Wammu.Events.EditEvent(index = event.m_itemIndex)
        wx.PostEvent(self.win, evt)

    def getColumnText(self, index, col):
        item = self.GetItem(index, col)
        return item.GetText()


    def OnGetItemText(self, item, col):
        if self.type == 'info':
            return self.values[item][col]
        elif self.type == 'memory':
            if col == 0:
                return self.values[item]['Location']
            elif col == 1:
                return self.values[item]['MemoryType']
            elif col == 2:
                return self.values[item]['Name']
#                return Wammu.Utils.GetMemoryEntryName(self.values[item])
            else:
                return self.values[item]['Number']
#                return Wammu.Utils.GetMemoryEntryNumber(self.values[item])
        elif self.type == 'call':
            if col == 0:
                return self.values[item]['Location']
            elif col == 1:
                return self.values[item]['MemoryType']
            elif col == 2:
                return self.values[item]['Name']
#                return Wammu.Utils.GetMemoryEntryName(self.values[item])
            else:
                return self.values[item]['Number']
#                return Wammu.Utils.GetMemoryEntryNumber(self.values[item])
                
        else:
            return 'Item %d, column %d' % (item, col)

    def OnGetItemAttr(self, item):
        if item % 2 == 1:
            return self.attr1
        else:
            return self.attr2


