import wx
import wxPython.utils
import wx.calendar
import wx.lib.timectrl
import wx.lib.intctrl
import Wammu.popupctl
import locale
import sys
import datetime
import time
import Wammu
import Wammu.Utils

def TextToTime(txt):
    hms = txt.split(':')
    return datetime.time(int(hms[0]), int(hms[1]), int(hms[2]))

def TextToDate(txt):
    ymd = txt.split('-')
    return datetime.date(int(ymd[0]), int(ymd[1]), int(ymd[2]))

def TimeToText(time):
    try:
        try:
            time = time.time()
        except:
            pass
        return time.isoformat()
    except:
        #FIXME: configurable
        return '9:00:00'

def DateToText(date):
    try:
        try:
            date = date.date()
        except:
            pass
        return date.isoformat()
    except:
        #FIXME: configurable
        return str(datetime.datetime.fromtimestamp(time.time() + 24*60*60).date())

class DateControl(Wammu.popupctl.wxPopupControl):
    """
    Date editor heavilly based on wxPython example - wxPopupControl.py
    """
    def __init__(self, parent, value):
        Wammu.popupctl.wxPopupControl.__init__(self, parent, value)

        self.win = wx.Window(self,-1,pos = (0,0),style = 0)
        self.cal = wx.calendar.CalendarCtrl(self.win,-1,pos = (0,0))

        bz = self.cal.GetBestSize()
        self.win.SetSize(bz)

        # This method is needed to set the contents that will be displayed
        # in the popup
        self.SetPopupContent(self.win)

        # Event registration for date selection
        wx.calendar.EVT_CALENDAR_DAY(self.cal,self.cal.GetId(),self.OnCalSelected)

    # Method called when a day is selected in the calendar
    def OnCalSelected(self,evt):
        self.PopDown()
        date = self.cal.GetDate()

        # Format the date that was selected for the text part of the control
        self.SetValue('%04d-%02d-%02d' % (date.GetYear(),
                                          date.GetMonth()+1,
                                          date.GetDay()))
        evt.Skip()

    # Method overridden from wxPopupControl
    # This method is called just before the popup is displayed
    # Use this method to format any controls in the popup
    def FormatContent(self):
        # I parse the value in the text part to resemble the correct date in
        # the calendar control
        txtValue = self.GetValue()
        dmy = txtValue.split('-')
        didSet = False
        if len(dmy) == 3:
            date = self.cal.GetDate()
            d = int(dmy[2])
            m = int(dmy[1]) - 1
            y = int(dmy[0])
            if d > 0 and d < 31:
                if m >= 0 and m < 12:
                    if y > 1000:
                        self.cal.SetDate(wxPython.utils.wxDateTimeFromDMY(d,m,y))
                        didSet = True
        if not didSet:
            self.cal.SetDate(wxPython.utils.wxDateTime_Today())


class DateTimeEdit(wx.Panel):
    """
    Generic class for static text with some edit control.
    """
    def __init__(self, parent, value): 
        wx.Panel.__init__(self, parent, -1)
        self.sizer = wx.FlexGridSizer(1, 3, 2, 2)
        self.sizer.AddGrowableCol(1)
        try:
            val = str(value.time())
        except:
            #FIXME: configurable
            val = '9:00:00'
        self.timeed = wx.lib.timectrl.TimeCtrl( self, -1, val, fmt24hr=True)
        try:
            val = str(value.date())
        except:
            #FIXME: configurable
            val = str(datetime.datetime.fromtimestamp(time.time() + 24*60*60).date())
        self.dateed = DateControl(self, val)
        self.SetValue(value)
        self.sizer.AddMany([ 
            (self.dateed, 0, wx.EXPAND),
            (self.timeed, 0, wx.EXPAND),
            ])
        self.sizer.Fit(self)
        self.SetAutoLayout(True)
        self.SetSizer(self.sizer)

    def GetValue(self):
        txtdate = self.dateed.GetValue()
        ymd = txtdate.split('-')
        txttime = self.timeed.GetValue()
        hms = txttime.split(':')
        return datetime.datetime(int(ymd[0]), int(ymd[1]), int(ymd[2]), int(hms[0]), int(hms[1]), int(hms[2]))

    def SetValue(self, value):
        try:
            val = str(value.time())
        except:
            #FIXME: configurable
            val = '9:00:00'
        self.timeed.SetValue(val)
        try:
            val = str(value.date())
        except:
            #FIXME: configurable
            val = str(datetime.datetime.fromtimestamp(time.time() + 24*60*60).date())
        self.dateed.SetValue(val)


class TextEdit(wx.Panel):
    """
    Generic class for static text with some edit control.
    """
    def __init__(self, parent): 
        wx.Panel.__init__(self, parent, -1)

    def PostInit(self, text, control):
        self.sizer = wx.FlexGridSizer(1, 3, 2, 2)
        self.sizer.AddGrowableCol(1)
        self.control = control
        self.sizer.AddMany([ 
            (wx.StaticText(self, -1, text),     0, wx.EXPAND),
            (10,10),
            (self.control,                      0, wx.EXPAND),
            ])
        self.sizer.Fit(self)
        self.SetAutoLayout(True)
        self.SetSizer(self.sizer)

    def GetValue(self):
        return self.control.GetValue()

    def SetValue(self, value):
        return self.control.SetValue(value)


class TextCombo(TextEdit):
    """
    Text + Combo edit control
    """
    def __init__(self, parent, text, value, choices): 
        TextEdit.__init__(self, parent)
        self.PostInit(text, wx.ComboBox(self, -1, value, choices = choices, style = wx.CB_READONLY))

class TextNumber(TextEdit):
    """
    Text + Spin edit control
    """
    def __init__(self, parent, text, value, min = 1, max = sys.maxint): 
        TextEdit.__init__(self, parent)
        self.PostInit(text, wx.SpinCtrl(self, -1, str(value), style = wx.SP_WRAP|wx.SP_ARROW_KEYS , min = min, max = max, initial = value))

class OneEdit(wx.Panel):
    """
    Text + Combo + editor for type specified by combo value
    """
    def __init__(self, parent, text, type, choices, value): 
        wx.Panel.__init__(self, parent, -1)
        self.sizer = wx.FlexGridSizer(1, 4, 2, 2)
        self.sizer.AddGrowableCol(1)
        self.sizer.AddGrowableCol(2)
        self.sizer.AddGrowableCol(3)
        self.text = wx.StaticText(self, -1, text)
        self.combo = wx.ComboBox(self, -1, type, choices = choices, style = wx.CB_READONLY)
        self.sizer.AddMany([ 
            (self.text,   0, wx.EXPAND|wx.ALL),
            (self.combo,  1, wx.EXPAND|wx.ALL),
            ])
        self.CreateEdit(type, value)
        self.sizer.Fit(self)
        self.SetAutoLayout(True)
        self.SetSizer(self.sizer)
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
        self.sizer.Remove(3)
        if hasattr(self, 'edit'):
            self.edit.Destroy()
            del self.edit

        if hasattr(self, 'edit2'):
            self.edit2.Destroy()
            del self.edit2

        self.edit2 = wx.StaticText(self, -1, '')
        if newt == 'text' or newt == 'phone' or newt == None:
            self.edit = wx.TextCtrl(self, -1, str(value), size = (200, -1))
        elif newt == 'bool':
            try:
                val = bool(value)
            except:
                val = False
            self.edit = wx.CheckBox(self, -1, '')
            self.edit.SetValue(val)
        elif newt == 'contact' or newt == 'category' or newt == 'number':
            try:
                val = int(value)
            except:
                val = 0
            self.edit = wx.lib.intctrl.IntCtrl(self, -1, val)
        elif newt == 'datetime':
            self.edit = wx.lib.timectrl.TimeCtrl( self, -1, TimeToText(value), fmt24hr=True)
            self.edit2.Destroy()
            self.edit2 = DateControl(self, DateToText(value))
        elif newt == 'date':
            self.edit = DateControl(self, DateToText(value))
        else:
            print 'warning: creating TextCtrl for %s' % newt
            self.edit = wx.TextCtrl(self, -1, str(value))
            
        self.sizer.AddMany([
            (self.edit,   1, wx.EXPAND|wx.ALL), 
            (self.edit2,  1, wx.EXPAND|wx.ALL)
            ])
       
    def OnChange(self, evt):
        self.CreateEdit(evt.GetString())
        self.sizer.SetSizeHints(self)

    def GetValue(self):
        t = Wammu.Utils.GetItemType(self.type)
        if t == 'date':
            return TextToDate(self.edit.GetValue())
        elif t == 'datetime':
            return datetime.datetime.combine(TextToDate(self.edit2.GetValue()), TextToTime(self.edit.GetValue()))
        else:
            return self.edit.GetValue()

    def GetType(self):
        return self.combo.GetValue()


class OkCancelMore(wx.Panel):
    """
    OK + Cancel + More buttons
    """
    def __init__(self, parent): 
        wx.Panel.__init__(self, parent, -1)
        self.sizer = wx.FlexGridSizer(1, 4, 2, 2)

        self.ok = wx.Button(self, wx.ID_OK, _('OK'))
        self.cancel = wx.Button(self, wx.ID_CANCEL, _('Cancel'))
        self.more = wx.Button(self, -1, _('More'))

        self.sizer.AddMany([ 
            (self.ok,       0, wx.EXPAND | wx.ALL),
            (self.cancel,   0, wx.EXPAND | wx.ALL),
            (self.more,     0, wx.EXPAND | wx.ALL),
            ])
        
        self.sizer.Fit(self)
        self.SetAutoLayout(True)
        self.SetSizer(self.sizer)


class GenericEditor(wx.Dialog):
    """
    Generic editor customised further by it's descendants
    """
    def __init__(self, parent, cfg, entry, internalname, name, location, type, typedefault, typename, typevalues, itemtypes ):
        if entry == {}:
            title = _('Creating new %s') % name
            wasempty = True
        else:
            title = _('Editing %s %s') % (name, location)
            wasempty = False

        wx.Dialog.__init__(self, parent, -1, title, style = wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)
        self.entry = entry
        self.type = type
        self.cfg = cfg
        self.internalname = internalname
        self.itemtypes = itemtypes
        self.sizer = wx.FlexGridSizer(3, 1, 2, 2)
        self.sizer.AddGrowableCol(0)
        list = []
        if wasempty:
            entry['Location'] = 0
            entry[type] = typedefault

        self.locationedit = TextNumber(self,  _('Location (0 = auto):'), entry['Location'], 0)
        self.typeedit = TextCombo(self, typename, entry[type], typevalues)
        
        wx.EVT_TEXT(self.typeedit.control, self.typeedit.control.GetId(), self.OnTypeChange)

        list.append((self.locationedit,   0, wx.EXPAND|wx.ALL, 2))
        list.append((self.typeedit,   0, wx.EXPAND|wx.ALL, 2))
        self.edits = []
        x = 0
        if wasempty:
            for x in range(3):
                e = OneEdit(self, '%d.' % (x + 1), '', self.itemtypes + [''] , '')
                self.edits.append(e)
                list.append((e, 0, wx.EXPAND|wx.ALL, 2))
        else:
            for i in entry['Entries']:
                e = OneEdit(self, '%d.' % (x + 1), i['Type'], self.itemtypes + [''] , i['Value'])
                self.edits.append(e)
                list.append((e, 0, wx.EXPAND|wx.ALL, 2))
                x = x + 1

        self.buttons = OkCancelMore(self)
        list.append((self.buttons, 0, wx.EXPAND|wx.ALL, 2))
                
        self.sizer.AddMany(list)
        self.sizer.Fit(self)
        self.SetAutoLayout(True)
        self.SetSizer(self.sizer)
        wx.EVT_BUTTON(self, wx.ID_OK, self.Okay)
        wx.EVT_BUTTON(self, self.buttons.more.GetId(), self.More)

    def OnTypeChange(self, evt):
        self.locationedit.SetValue(0)

    def More(self, evt):
        self.sizer.Remove(len(self.edits) + 2)
        
        e = OneEdit(self, '%d.' % (len(self.edits) + 1), '', self.itemtypes + [''] , '')
        self.edits.append(e)

        self.sizer.AddMany([
            (e, 0, wx.EXPAND|wx.ALL,2), 
            (self.buttons, 0, wx.EXPAND|wx.ALL, 2)
            ])
        self.sizer.Fit(self)

    def Okay(self, evt):       
        v = []
        for x in self.edits:
            i = {}
            t = x.GetType()
            if t != '':
                i['Type'] = t
                val = x.GetValue()
                datatype = Wammu.Utils.GetItemType(t)
                if datatype == 'text' or datatype == 'phone':
                    if not wx.USE_UNICODE:
                        i['Value'] = unicode(val, locale.getdefaultlocale()[1])
                    else:
                        i['Value'] = val
                else:
                    i['Value'] = val
                v.append(i)

        self.entry['Entries'] = v
        self.entry[self.type] = self.typeedit.GetValue()
        self.entry['Location'] = self.locationedit.GetValue()
        self.EndModal(wx.ID_OK)

class ContactEditor(GenericEditor):
    def __init__(self, parent, cfg, entry):
        if entry == {}:
            location = ''
        else:
            location = '%s:%d' % (entry['MemoryType'], entry['Location'])
        GenericEditor.__init__(self, parent, cfg, entry, 'contact',  _('contact'), location, 'MemoryType', 'SM', _('Memory type'), Wammu.ContactMemoryTypes, Wammu.MemoryValueTypes)

class CalendarEditor(GenericEditor):
    def __init__(self, parent, cfg, entry):
        if entry == {}:
            location = ''
        else:
            location = '%d' % entry['Location']
        GenericEditor.__init__(self, parent, cfg, entry, 'calendar',  _('calendar event'), location, 'Type', 'MEETING', _('Event type'), Wammu.CalendarTypes, Wammu.CalendarValueTypes)

class TodoEditor(GenericEditor):
    def __init__(self, parent, cfg, entry):
        if entry == {}:
            location = ''
        else:
            location = '%d' % entry['Location']
        GenericEditor.__init__(self, parent, cfg, entry, 'todo',  _('todo item'), location, 'Priority', 'Medium', _('Priority'), Wammu.TodoPriorities, Wammu.TodoValueTypes)
