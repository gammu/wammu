import wx

class OneEdit(wx.Panel):
    def __init__(self, parent, text, type, choices, value): 
        wx.Panel.__init__(self, parent, -1, title)
        self.sizer = wx.GridSizer(1, 3, 2, 2)  # rows, cols, hgap, vgap
        self.sizer.AddMany([ 
            (wx.StaticText(self, -1, text),   0, wx.EXPAND),
            (wx.ComboBox(self, -1, type, choices, style = wx.CB_READONLY),   0, wx.EXPAND),
            (wx.TextCtrl(self, -1, value),   0, wx.EXPAND)
            ])
        
        self.sizer.Fit(self)
        self.SetAutoLayout(True)
        self.SetSizer(self.sizer)


class ContactEditor(wx.Dialog):
    def __init__(self, parent, entry):
        wx.Dialog.__init__(self, parent, -1, _('Editing contact %d from %s') % (entry['Location'], entry['MemoryType']))
        self.sizer = wx.GridSizer(3, 1, 2, 2)  # rows, cols, hgap, vgap
        list = [
            (wx.StaticText(self, -1, _('Location: %d') % entry['Location']),   0, wx.EXPAND),
            (wx.StaticText(self, -1, _('Memory type: %s') % entry['MemoryType']),   0, wx.EXPAND),
            ]
        self.sizer.AddMany(list)
        self.sizer.Fit(self)
        self.SetAutoLayout(True)
        self.SetSizer(self.sizer)
