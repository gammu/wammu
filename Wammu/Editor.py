import wx
import Wammu
import Wammu.Utils

class OneEdit(wx.Panel):
    def __init__(self, parent, text, type, choices, value): 
        wx.Panel.__init__(self, parent, -1)
        self.sizer = wx.GridSizer(1, 3, 2, 2)  # rows, cols, hgap, vgap
        self.combo = wx.ComboBox(self, -1, type, choices = choices, style = wx.CB_READONLY, size = (100,0))
        self.edit = wx.TextCtrl(self, -1, value, size = (100,0))
        self.sizer.AddMany([ 
            (wx.StaticText(self, -1, text),   0, wx.EXPAND),
            (self.combo,   0, wx.EXPAND),
            (self.edit,   0, wx.EXPAND)
            ])
        
        self.sizer.Fit(self)
        self.SetAutoLayout(True)
        self.SetSizer(self.sizer)

class OkCancelMoreFew(wx.Panel):
    def __init__(self, parent): 
        wx.Panel.__init__(self, parent, -1)
        self.sizer = wx.GridSizer(1, 4, 2, 2)  # rows, cols, hgap, vgap

        self.ok = wx.Button(self, wx.ID_OK, _('OK'))
        self.cancel = wx.Button(self, wx.ID_CANCEL, _('Cancel'))
        self.more = wx.Button(self, 1001, _('More'))
        self.fewer = wx.Button(self, 1002, _('Fewer'))

        self.sizer.AddMany([ 
            (self.ok,   0, wx.EXPAND),
            (self.cancel,   0, wx.EXPAND),
            (self.more,   0, wx.EXPAND),
            (self.fewer,   0, wx.EXPAND),
            ])
        
        self.sizer.Fit(self)
        self.SetAutoLayout(True)
        self.SetSizer(self.sizer)


class ContactEditor(wx.Dialog):
    def __init__(self, parent, sm, entry):
        wx.Dialog.__init__(self, parent, -1, _('Editing contact %d from %s') % (entry['Location'], entry['MemoryType']), style = wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)
        self.sm = sm
        self.entry = entry
        self.sizer = wx.GridSizer(3, 1, 2, 2)  # rows, cols, hgap, vgap
        list = [
            (wx.StaticText(self, -1, _('Location: %d') % entry['Location']),   0, wx.EXPAND),
            (wx.StaticText(self, -1, _('Memory type: %s') % entry['MemoryType']),   0, wx.EXPAND),
            ]
        self.edits = []
        x = 0
        for i in entry['Values']:
            x = x + 1
            e = OneEdit(self, '%d.' % x, i['Type'], Wammu.MemoryValueTypes , str(i['Value']))
            self.edits.append(e)
            list.append((e, 0, wx.EXPAND))

        self.buttons = OkCancelMoreFew(self)
        list.append((self.buttons, 0, wx.EXPAND))
                
        self.sizer.AddMany(list)
        self.sizer.Fit(self)
        self.SetAutoLayout(True)
        self.SetSizer(self.sizer)
        wx.EVT_BUTTON(self, wx.ID_OK, self.Okay)

    def Okay(self, evt):       
        v = []
        for x in self.edits:
            i = {}
            i['Type'] = x.combo.GetValue()
            i['Value'] = x.edit.GetValue()
            v.append(i)
        self.entry['Values'] = v
        Wammu.Utils.GetMemoryEntryName(self.entry)
        Wammu.Utils.GetMemoryEntryNumber(self.entry)
        self.EndModal(wx.ID_OK)
