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
#        wx.EVT_LIST_DELETE_ITEM(self, self.GetId(), self.OnItemDeleted)
        wx.EVT_LIST_KEY_DOWN(self, self.GetId(), self.OnKey)
        wx.EVT_LIST_COL_CLICK(self, self.GetId(), self.OnColClick)
        wx.lib.mixins.listctrl.ListCtrlAutoWidthMixin.__init__(self)

    def ShowHeaders(self):
        if self.type == 'info':
            self.InsertColumn(0, 'Name')
            self.InsertColumn(1, 'Value')
            self.keys = (0, 1)
        elif self.type == 'memory':
            self.InsertColumn(0, 'Location')
            self.InsertColumn(1, 'Memory')
            self.InsertColumn(2, 'Name')
            self.InsertColumn(3, 'Number')
            self.keys = ('Location', 'MemoryType', 'Name', 'Number')
        elif self.type == 'call':
            self.InsertColumn(0, 'Location')
            self.InsertColumn(1, 'Type')
            self.InsertColumn(2, 'Name')
            self.InsertColumn(3, 'Number')
            self.keys = ('Location', 'MemoryType', 'Name', 'Number')

        # resize columns to fit content
        
        # FIXME: this should be acquired better!
        spc = 10
        cnt = self.GetColumnCount()
        
        max = [0] * cnt
        for i in range(cnt):
            size = self.GetTextExtent(self.GetColumn(i).GetText())
            # 16 bellow is for sort arrrow
            if (size[0] + 16 > max[i]):
                max[i] = size[0] + 16
            
        for x in self.values:
            for i in range(cnt):
                size = self.GetTextExtent(str(x[self.keys[i]]))
                if (size[0] > max[i]):
                    max[i] = size[0]
        for i in range(cnt - 1):
            self.SetColumnWidth(i, max[i] + spc)
        self.resizeLastColumn(max[cnt - 1] + spc)
    
    def Sorter(self, i1, i2):
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
        top = self.GetTopItem() 
        self.RefreshItems(top, top + self.GetCountPerPage())

    def OnKey(self, evt):
        if evt.GetKeyCode() == wx.WXK_DELETE:
            evt = Wammu.Events.DeleteEvent(index = evt.m_itemIndex)
            wx.PostEvent(self.win, evt)
        
    def OnColClick(self, evt):
        self.Resort(evt.GetColumn())
        
    def OnItemSelected(self, event):
        evt = Wammu.Events.ShowEvent(index = event.m_itemIndex)
        wx.PostEvent(self.win, evt)

    def OnItemActivated(self, event):
        evt = Wammu.Events.EditEvent(index = event.m_itemIndex)
        wx.PostEvent(self.win, evt)

    def OnItemDeleted(self, event):
        evt = Wammu.Events.DeleteEvent(index = event.m_itemIndex)
        wx.PostEvent(self.win, evt)

    def getColumnText(self, index, col):
        item = self.GetItem(index, col)
        return item.GetText()



    def OnGetItemText(self, item, col):
        return self.values[item][self.keys[col]]

    def OnGetItemAttr(self, item):
        if item % 2 == 1:
            return self.attr1
        else:
            return self.attr2


