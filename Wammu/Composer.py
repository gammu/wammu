import wx
import wx.lib.rcsizer
import wx.lib.editor.editor
import wx.lib.mixins.listctrl 

class AutoSizeList(wx.ListCtrl, wx.lib.mixins.listctrl.ListCtrlAutoWidthMixin):
    def __init__(self, parent, firstcol):
        wx.ListCtrl.__init__(self, parent, -1, style=wx.LC_REPORT | wx.LC_HRULES | wx.LC_VRULES | wx.LC_SINGLE_SEL | wx.SUNKEN_BORDER, size = (200, 200))
        self.InsertColumn(0, firstcol)
        wx.lib.mixins.listctrl.ListCtrlAutoWidthMixin.__init__(self)

class GenericEditor(wx.Panel):
    """
    Generic class for static text with some edit control.
    """
    def __init__(self, parent, part): 
        wx.Panel.__init__(self, parent, -1)
        self.part = part

class TextEditor(GenericEditor):
    def __init__(self, parent, part): 
        GenericEditor.__init__(self, parent, part)
        self.sizer = wx.lib.rcsizer.RowColSizer()

        self.edit = wx.TextCtrl(self, -1, style=wx.TE_MULTILINE)
        
        
        self.sizer.Add(self.edit, pos = (0,0), flag = wx.EXPAND, colspan = 4)
        self.sizer.AddGrowableCol(0)
        self.sizer.AddGrowableRow(0)
    
        self.leninfo = wx.StaticText(self, -1, _('Typed %d characters') % 0, style = wx.ALIGN_LEFT)
        self.sizer.Add(self.leninfo, pos = (3, 1), flag = wx.ALIGN_TOP | wx.ALIGN_RIGHT)
    
        wx.EVT_TEXT(self.edit, self.edit.GetId(), self.TextChanged)
        if self.part.has_key('Buffer'):
            self.edit.SetValue(self.part['Buffer'])

        self.sizer.Fit(self)
        self.SetAutoLayout(True)
        self.SetSizer(self.sizer)
        
    def TextChanged(self, evt = None):
        self.leninfo.SetLabel( _('Typed %d characters') % len(self.edit.GetValue()))

    def GetValue(self):
        # FIXME
        self.part['ID'] = 'Text'
        self.part['Buffer'] = self.edit.GetValue()
        return self.part

class PredefinedAnimEditor(GenericEditor):
    def __init__(self, parent, part): 
        GenericEditor.__init__(self, parent, part)
        self.sizer = wx.lib.rcsizer.RowColSizer()

        self.sizer.Fit(self)
        self.SetAutoLayout(True)
        self.SetSizer(self.sizer)

    def GetValue(self):
        return self.part

SMSParts = [
# FIXME: should support more types...
#   ID, display text, match types, editor, init type
    (0, _('Text'), ['Text', 'ConcatenatedTextLong', 'ConcatenatedAutoTextLong', 'ConcatenatedTextLong16bit', 'ConcatenatedAutoTextLong16bit'], TextEditor, 'Text'),
    (1, _('Predefined animation'), ['EMSPredefinedAnimation'], PredefinedAnimEditor, 'EMSPredefinedAnimation'),
    ]

class SMSComposer(wx.Dialog):
    def __init__(self, parent, cfg, entry, type = 'send', addtext = True):
        wx.Dialog.__init__(self, parent, -1, _('Composing SMS'), style = wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)
        self.entry = entry
        if not entry.has_key('SMSInfo'):
            entry['SMSInfo'] = {}
            entry['SMSInfo']['Entries'] = []
            if entry.has_key('Text'):
                entry['SMSInfo']['Entries'].append({'ID': 'Text', 'Buffer': entry['Text']})
            elif addtext:
                entry['SMSInfo']['Entries'].append({'ID': 'Text', 'Buffer': ''})
        self.cfg = cfg
        self.sizer = wx.lib.rcsizer.RowColSizer()
      
        self.editor = wx.StaticText(self, -1, _('Create new message by adding part to left list...'), size = (-1, 200))
      
        self.send = wx.CheckBox(self, -1, _('Send message'))
        self.send.SetValue(type == 'send')
        self.save = wx.CheckBox(self, -1, _('Save into folder'))
        self.save.SetValue(type == 'save')
        self.folder = wx.SpinCtrl(self, -1, '2', style = wx.SP_WRAP|wx.SP_ARROW_KEYS , min = 0, max = 3, initial = 2)

        self.sizer.Add(self.send, pos = (1,1), flag = wx.ALIGN_CENTER)
        self.sizer.Add(self.save, pos = (1,6), flag = wx.ALIGN_CENTER)
        self.sizer.Add(self.folder, pos = (1,7), flag = wx.ALIGN_CENTER)
        
        self.current = AutoSizeList(self, _('Parts of current message'))
        self.available = AutoSizeList(self, _('Available message parts'))
        # FIXME: add icons?

        self.addbut = wx.Button(self, -1, _('<<< Add <<<'))
        self.delbut = wx.Button(self, -1, _('>>> Delete'))
        wx.EVT_BUTTON(self, self.addbut.GetId(), self.AddPressed)
        wx.EVT_BUTTON(self, self.delbut.GetId(), self.DeletePressed)

        
        self.sizer.Add(self.current, pos = (3,1), flag = wx.EXPAND, colspan = 2, rowspan = 2)
        self.sizer.Add(self.addbut, pos = (3,4), flag = wx.ALIGN_CENTER)
        self.sizer.Add(self.delbut, pos = (4,4), flag = wx.ALIGN_CENTER)
        self.sizer.Add(self.available, pos = (3,6), flag = wx.EXPAND, colspan = 2, rowspan = 2)
        
        self.upbut = wx.Button(self, -1, _('Up'))
        self.dnbut = wx.Button(self, -1, _('Down'))
        
        self.sizer.Add(self.upbut, pos = (6,1), flag = wx.ALIGN_CENTER)
        self.sizer.Add(self.dnbut, pos = (6,2), flag = wx.ALIGN_CENTER)

        wx.EVT_BUTTON(self, self.upbut.GetId(), self.UpPressed)
        wx.EVT_BUTTON(self, self.dnbut.GetId(), self.DnPressed)
        
        self.sizer.Add(self.editor, pos = (8,1), flag = wx.EXPAND, colspan = 7)

        
        self.ok = wx.Button(self, wx.ID_OK, _('OK'))
        self.cancel = wx.Button(self, wx.ID_CANCEL, _('Cancel'))
        self.sizer.Add(self.ok, pos = (10, 1), flag = wx.ALIGN_CENTER, colspan = 2)
        self.sizer.Add(self.cancel, pos = (10, 6), flag = wx.ALIGN_CENTER, colspan = 2)

        wx.EVT_BUTTON(self, wx.ID_OK, self.Okay)

        self.sizer.AddSpacer(5,5, pos=(11,8))
        self.sizer.AddGrowableCol(1)
        self.sizer.AddGrowableRow(3)
        self.sizer.AddGrowableRow(8)
        self.sizer.AddGrowableCol(5)
        self.sizer.Fit(self)
        self.SetAutoLayout(True)
        self.SetSizer(self.sizer)

        self.prevedit = -1
        self.availsel = -1

        wx.EVT_LIST_ITEM_SELECTED(self.current, self.current.GetId(), self.CurrentSelected)
        wx.EVT_LIST_ITEM_SELECTED(self.available, self.available.GetId(), self.AvailableSelected)

        for x in SMSParts:
            self.available.InsertImageStringItem(x[0], x[1], x[0])
        self.available.SetItemState(0, wx.LIST_STATE_FOCUSED | wx.LIST_STATE_SELECTED, wx.LIST_STATE_FOCUSED | wx.LIST_STATE_SELECTED)

        self.GenerateCurrent()

    def GenerateCurrent(self, select = 0):
        self.current.DeleteAllItems()
        for i in range(len(self.entry['SMSInfo']['Entries'])):
            found = False
            x = self.entry['SMSInfo']['Entries'][i]
            for p in SMSParts:
                if x['ID'] in p[2]:
                    self.current.InsertImageStringItem(i, p[1], p[0])
                    found = True
                    break
            if not found:
                self.current.InsertImageStringItem(i, _('Not supported id: %s') % x['ID'], -1)
                print 'Not supported id: %s' % x['ID']
    
        count = self.current.GetItemCount()
            
        if count > 0:
            while select > count:
                select = select - 1
            self.current.SetItemState(select, wx.LIST_STATE_FOCUSED | wx.LIST_STATE_SELECTED, wx.LIST_STATE_FOCUSED | wx.LIST_STATE_SELECTED)

    def AvailableSelected(self, event):
        self.availsel = event.m_itemIndex

    def CurrentSelected(self, event):
        self.StoreEdited()
        if hasattr(self, 'editor'):
            self.editor.Destroy()
            del self.editor

        found = False
        for p in SMSParts:
            if self.entry['SMSInfo']['Entries'][event.m_itemIndex]['ID'] in p[2]:
                self.editor = p[3](self, self.entry['SMSInfo']['Entries'][event.m_itemIndex])
                self.sizer.Add(self.editor, pos = (8,1), flag = wx.EXPAND, colspan = 7)
                found = True
                break
        if not found:
            self.editor = wx.StaticText(self, -1, _('No editor available for type %s') % self.entry['SMSInfo']['Entries'][event.m_itemIndex]['ID'])
            self.sizer.Add(self.editor, pos = (8,1), flag = wx.EXPAND, colspan = 7)
            self.prevedit = -1
        else:
            self.prevedit = event.m_itemIndex

    def UpPressed(self, evt):
        if self.prevedit == -1:
            return
        next = self.prevedit - 1
        if next < 0:
            return
        print 'switch %d and %d' % (self.prevedit, next)
        self.StoreEdited()
        v = self.entry['SMSInfo']['Entries'][self.prevedit]
        self.entry['SMSInfo']['Entries'][self.prevedit] = self.entry['SMSInfo']['Entries'][next]
        self.entry['SMSInfo']['Entries'][next] = v
        self.prevedit = -1
        self.GenerateCurrent(next)

    def DnPressed(self, evt):
        if self.prevedit == -1:
            return
        next = self.prevedit + 1
        if next >= self.current.GetItemCount():
            return
        self.StoreEdited()
        v = self.entry['SMSInfo']['Entries'][self.prevedit]
        self.entry['SMSInfo']['Entries'][self.prevedit] = self.entry['SMSInfo']['Entries'][next]
        self.entry['SMSInfo']['Entries'][next] = v
        self.prevedit = -1
        self.GenerateCurrent(next)

    def DeletePressed(self, evt):
        if self.prevedit == -1:
            return
        self.StoreEdited()
        del self.entry['SMSInfo']['Entries'][self.prevedit]
        self.GenerateCurrent(max(self.prevedit - 1, 0))

    def AddPressed(self, evt):
        if self.availsel == -1 or self.prevedit == -1:
            return
        v = {'ID': SMSParts[self.availsel][4]}
        self.StoreEdited()
        self.entry['SMSInfo']['Entries'].insert(self.prevedit + 1, v)
        next = self.prevedit + 1
        self.prevedit = -1
        self.GenerateCurrent(next)

    def StoreEdited(self):
        if self.prevedit != -1:
            self.entry['SMSInfo']['Entries'][self.prevedit] = self.editor.GetValue()
            
    def Okay(self, evt):       
        self.StoreEdited()
        self.EndModal(wx.ID_OK)
