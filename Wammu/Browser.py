import wx
import Wammu
import Wammu.Events
import Wammu.Utils
import gammu
from Wammu.Paths import *

import wx.lib.mixins.listctrl 

class Browser(wx.ListCtrl, wx.lib.mixins.listctrl.ListCtrlAutoWidthMixin):
    def __init__(self, parent, win):
        wx.ListCtrl.__init__(self, parent, -1,
                            style=wx.LC_REPORT|wx.LC_VIRTUAL|wx.LC_HRULES|wx.LC_VRULES)
        self.win = win

        self.attr1 = wx.ListItemAttr()

        self.attr2 = wx.ListItemAttr()
        self.attr2.SetBackgroundColour('light blue')

        il = wx.ImageList(16, 16)
        self.downarrow = il.Add(wx.Bitmap(MiscPath('downarrow')))
        self.uparrow = il.Add(wx.Bitmap(MiscPath('uparrow')))
        self.AssignImageList(il, wx.IMAGE_LIST_SMALL)

        wx.EVT_LIST_ITEM_SELECTED(self, self.GetId(), self.OnItemSelected)
        wx.EVT_LIST_ITEM_ACTIVATED(self, self.GetId(), self.OnItemActivated)
        wx.EVT_LIST_COL_CLICK(self, self.GetId(), self.OnColClick)
        wx.lib.mixins.listctrl.ListCtrlAutoWidthMixin.__init__(self)

    def ShowHeaders(self):
        if self.type == 'info':
            self.InsertColumn(0, 'Name')
            self.InsertColumn(1, 'Value')
            self.sortkeys = (0, 1)
            self.dispkeys = (0, 1)
#            self.SetColumnWidth(0, 100)
#            self.SetColumnWidth(1, 200)
            self.SetColumnWidth(0, wx.LIST_AUTOSIZE)
#            self.SetColumnWidth(1, wx.LIST_AUTOSIZE)
        elif self.type == 'memory':
            self.InsertColumn(0, 'Location')
            self.InsertColumn(1, 'Memory')
            self.InsertColumn(2, 'Name')
            self.InsertColumn(3, 'Number')
            self.sortkeys = ('Location', 'MemoryType', 'Name', 'Number')
            self.dispkeys = ('Location', 'MemoryType', 'Name', 'Number')
            self.SetColumnWidth(0, wx.LIST_AUTOSIZE)
            self.SetColumnWidth(1, wx.LIST_AUTOSIZE)
            self.SetColumnWidth(2, wx.LIST_AUTOSIZE)
            self.SetColumnWidth(3, wx.LIST_AUTOSIZE)
        elif self.type == 'call':
            self.InsertColumn(0, 'Location')
            self.InsertColumn(1, 'Type')
            self.InsertColumn(2, 'Name')
            self.InsertColumn(3, 'Number')
            self.sortkeys = ('Location', 'MemoryType', 'Name', 'Number')
            self.dispkeys = ('Location', 'MemoryType', 'Name', 'Number')
            self.SetColumnWidth(0, wx.LIST_AUTOSIZE)
            self.SetColumnWidth(1, wx.LIST_AUTOSIZE)
            self.SetColumnWidth(2, wx.LIST_AUTOSIZE)
            self.SetColumnWidth(3, wx.LIST_AUTOSIZE)
        self.resizeLastColumn(0)
    
    def Sorter(self, i1, i2):
        if self.sortkey == 'Name':
            print '"%s" vs "%s"' % (repr(i1[self.sortkey]), repr(i2[self.sortkey]))
        return self.sortorder * cmp(i1[self.sortkey], i2[self.sortkey])
    
    def Change(self, type, values):
        self.type = type
        self.values = values
        self.sortkey = ''
        self.ClearAll()
        self.SetItemCount(len(values))
        self.ShowHeaders()
        self.Resort(0)

    def Resort(self, col):
        # find keys and order
        nextsort = self.sortkeys[col]
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
            image = self.uparrow
        else:
            image = self.downarrow
        self.SetColumnImage(col, image)

        # refresh displayed items
        top = self.GetTopItem() 
        self.RefreshItems(top, top + self.GetCountPerPage())

    def OnColClick(self, evt):
        self.Resort(evt.GetColumn())
        
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
        return self.values[item][self.dispkeys[col]]

    def OnGetItemAttr(self, item):
        if item % 2 == 1:
            return self.attr1
        else:
            return self.attr2


