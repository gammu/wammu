import wx
import wx.lib.intctrl
import locale
import Wammu
import Wammu.Utils

class TextCombo(wx.Panel):
    def __init__(self, parent, text, value, choices): 
        wx.Panel.__init__(self, parent, -1)
        self.sizer = wx.FlexGridSizer(1, 3, 2, 2)
        self.sizer.AddGrowableCol(1)
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
        self.sizer = wx.FlexGridSizer(1, 3, 2, 2)
        self.sizer.AddGrowableCol(1)
        self.sizer.AddGrowableCol(2)
        self.SetSizer(self.sizer)
        self.text = wx.StaticText(self, -1, text)
        self.edit = wx.TextCtrl(self, -1, str(value))
        self.combo = wx.ComboBox(self, -1, type, choices = choices, style = wx.CB_READONLY)
        self.sizer.AddMany([ 
            (self.text,   0, wx.EXPAND),
            (self.combo,  0, wx.EXPAND),
            (10,10)
            ])
        self.CreateEdit(type, value)
#        self.sizer.Fit(self)
        
        wx.EVT_TEXT(self.combo, self.combo.GetId(), self.OnChange)
       
    def CreateEdit(self, newtype, value = None):       
        if value == None and hasattr(self, 'edit'):
            value = self.edit.GetValue()

        if hasattr(self, 'type'):
            oldt = Wammu.Utils.GetItemType(self.type)
        else:
            oldt = ''
        newt = Wammu.Utils.GetItemType(newtype)
        
        self.type = newtype
        if oldt == newt:
            return

        self.sizer.Remove(2)
        if hasattr(self, 'edit'):
            self.edit.Destroy()
            del self.edit

        if newt == 'text' or newt == 'phone' or newt == None:
            self.edit = wx.TextCtrl(self, -1, str(value))
        elif newt == 'bool':
            try:
                val = bool(value)
            except:
                val = False
            self.edit = wx.CheckBox(self, -1, value)
        elif newt == 'contact' or newt == 'category' or newt == 'number':
            try:
                val = int(value)
            except:
                val = 0
            self.edit = wx.lib.intctrl.IntCtrl(self, -1, val)
        else:
            print 'warning, creating TextCtrl for %s' % newt
            self.edit = wx.TextCtrl(self, -1, str(value))
            
        self.sizer.AddMany([(self.edit,   0, wx.EXPAND)])
        # nice hack, isnt' it? :-)
        self.SetSize(self.GetSize())
       
    def OnChange(self, evt):
        self.CreateEdit(evt.GetString())

class OkCancelMore(wx.Panel):
    def __init__(self, parent): 
        wx.Panel.__init__(self, parent, -1)
        self.sizer = wx.FlexGridSizer(1, 4, 2, 2)

        self.ok = wx.Button(self, wx.ID_OK, _('OK'))
        self.cancel = wx.Button(self, wx.ID_CANCEL, _('Cancel'))
        self.more = wx.Button(self, -1, _('More'))

        self.sizer.AddMany([ 
            (self.ok,   0, wx.EXPAND),
            (self.cancel,   0, wx.EXPAND),
            (self.more,   0, wx.EXPAND),
            ])
        
        self.sizer.Fit(self)
        self.SetAutoLayout(True)
        self.SetSizer(self.sizer)


class ContactEditor(wx.Dialog):
    def __init__(self, parent, sm, entry):
        if entry == {}:
            title = _('Creating new contact')
        else:
            title = _('Editing contact %d from %s') % (entry['Location'], entry['MemoryType'])
        wx.Dialog.__init__(self, parent, -1, title, style = wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)
        self.sm = sm
        self.entry = entry
        self.sizer = wx.FlexGridSizer(3, 1, 2, 2)
        self.sizer.AddGrowableCol(0)
        if entry == {}:
            list = [
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
        if entry == {}:
            for x in range(3):
                e = OneEdit(self, '%d.' % (x + 1), '', Wammu.MemoryValueTypes + [''] , '')
                self.edits.append(e)
                list.append((e, 0, wx.EXPAND))
        else:
            for i in entry['Values']:
                x = x + 1
                e = OneEdit(self, '%d.' % x, i['Type'], Wammu.MemoryValueTypes + [''] , str(i['Value']))
                self.edits.append(e)
                list.append((e, 0, wx.EXPAND))

        self.buttons = OkCancelMore(self)
        list.append((self.buttons, 0, wx.EXPAND))
                
        self.sizer.AddMany(list)
        self.sizer.Fit(self)
        self.SetAutoLayout(True)
        self.SetSizer(self.sizer)
        wx.EVT_BUTTON(self, wx.ID_OK, self.Okay)
        wx.EVT_BUTTON(self, self.buttons.more.GetId(), self.More)

    def More(self, evt):
        self.sizer.Remove(len(self.edits) + 2)
        
        e = OneEdit(self, '%d.' % (len(self.edits) + 1), '', Wammu.MemoryValueTypes + [''] , '')
        self.edits.append(e)

        self.sizer.AddMany([(e, 0, wx.EXPAND), (self.buttons, 0, wx.EXPAND)])
        self.sizer.Fit(self)

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
        self.EndModal(wx.ID_OK)
