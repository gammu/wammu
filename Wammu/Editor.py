import wx
import locale
import Wammu
import Wammu.Utils

class TextCombo(wx.Panel):
    def __init__(self, parent, text, value, choices): 
        wx.Panel.__init__(self, parent, -1)
        self.sizer = wx.GridSizer(1, 3, 2, 2)  # rows, cols, hgap, vgap
        self.combo = wx.ComboBox(self, -1, value, choices = choices, style = wx.CB_READONLY)
        self.sizer.AddMany([ 
            (wx.StaticText(self, -1, text),   0, wx.EXPAND),
            (self.combo,   4, wx.EXPAND),
            ])
        
        self.sizer.Fit(self)
        self.SetAutoLayout(True)
        self.SetSizer(self.sizer)

class OneEdit(wx.Panel):
    def __init__(self, parent, text, type, choices, value): 
        wx.Panel.__init__(self, parent, -1)
        self.sizer = wx.GridSizer(1, 3, 2, 2)  # rows, cols, hgap, vgap
        self.combo = wx.ComboBox(self, -1, type, choices = choices, style = wx.CB_READONLY)
        self.edit = wx.TextCtrl(self, -1, value)
        self.sizer.AddMany([ 
            (wx.StaticText(self, -1, text),   0, wx.EXPAND),
            (self.combo,   4, wx.EXPAND),
            (self.edit,   4, wx.EXPAND)
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
        if entry == None:
            list [
                (wx.StaticText(self, -1, _('Creating new entry')),   0, wx.EXPAND)
                ]
            self.mt = TextCombo(self, _('Memory type:'), 'SM', Wammu.ContactMemoryTypes)
        else:
            list = [
                (wx.StaticText(self, -1, _('Location: %d') % entry['Location']),   0, wx.EXPAND)
                ]
            self.mt = TextCombo(self, _('Memory type:'), entry['MemoryType'], Wammu.ContactMemoryTypes)
        list.append((self.mt,   0, wx.EXPAND))
        self.edits = []
        x = 0
        if entry == None:
            for x in seq(2):
                e = OneEdit(self, '%d.' % x, '', Wammu.MemoryValueTypes + [''] , '')
                self.edits.append(e)
                list.append((e, 0, wx.EXPAND))
        else:
            for i in entry['Values']:
                x = x + 1
                e = OneEdit(self, '%d.' % x, i['Type'], Wammu.MemoryValueTypes + [''] , str(i['Value']))
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
            t = x.combo.GetValue()
            if t != '':
                i['Type'] = t
                val = x.edit.GetValue()
                if t[:4] == 'Text' or t[:6] == 'Number':
                    if not wx.USE_UNICODE:
                        i['Value'] = unicode(val, locale.getdefaultlocale()[1])
                    else:
                        i['Value'] = val
                elif t == 'Date':
                    # FIXME: generate datetime here...
                    i['Value'] = val
                else:
                    if val.isdigit():
                        i['Value'] = int(val)
                    else:
                        # FIXME: we hope, that lower level handles this correctly
                        i['Value'] = val
                v.append(i)

        self.entry['Values'] = v
        self.entry['MemoryType'] = self.mt.combo.GetValue()
        Wammu.Utils.GetMemoryEntryName(self.entry)
        Wammu.Utils.GetMemoryEntryNumber(self.entry)
        self.EndModal(wx.ID_OK)
