import wx
import Wammu

class Settings(wx.Dialog): 
    def __init__(self, parent, config):
        wx.Dialog.__init__(self, parent, -1, _('Settings'), style = wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)
        self.sizer = wx.FlexGridSizer(6, 2, 5, 5)
        self.sizer.AddGrowableCol(1)
        
        self.config = config

        self.editdev = wx.ComboBox(self, -1, config.Read('/Gammu/Device', Wammu.Devices[0]), choices = Wammu.Devices, size = (150, -1))
        self.editconn = wx.ComboBox(self, -1, config.Read('/Gammu/Connection', Wammu.Connections[0]), choices = Wammu.Connections, size = (150, -1))
        self.editmodel = wx.ComboBox(self, -1, config.Read('/Gammu/Model', Wammu.Models[0]), choices = Wammu.Models, size = (150, -1))
        self.editsync = wx.ComboBox(self, -1, config.Read('/Gammu/SyncTime', 'no'), choices = ['yes', 'no'], style = wx.CB_READONLY, size = (150, -1))
        self.editlock = wx.ComboBox(self, -1, config.Read('/Gammu/LockDevice', 'no'), choices = ['yes', 'no'], style = wx.CB_READONLY, size = (150, -1))
        self.editinfo = wx.ComboBox(self, -1, config.Read('/Gammu/StartInfo', 'no'), choices = ['yes', 'no'], style = wx.CB_READONLY, size = (150, -1))
        self.editdebug = wx.ComboBox(self, -1, config.Read('/Debug/Show', 'no'), choices = ['yes', 'no'], style = wx.CB_READONLY, size = (150, -1))
        self.editauto = wx.ComboBox(self, -1, config.Read('/Wammu/AutoConnect', 'no'), choices = ['yes', 'no'], style = wx.CB_READONLY, size = (150, -1))
        v = config.ReadInt('/Wammu/ScaleImage', 1)
        self.editscale = wx.SpinCtrl(self, -1, str(v), style = wx.SP_WRAP|wx.SP_ARROW_KEYS, min = 1, max = 20, initial = v, size = (150, -1))

        self.sizer.AddMany([ 
            (wx.StaticText(self, -1, _('Device')), 0, wx.EXPAND),
            (self.editdev, 0, wx.EXPAND),

            (wx.StaticText(self, -1, _('Connection')), 0, wx.EXPAND),
            (self.editconn, 0, wx.EXPAND),

            (wx.StaticText(self, -1, _('Model (empty = auto)')), 0, wx.EXPAND),
            (self.editmodel, 0, wx.EXPAND),

            (wx.StaticText(self, -1, _('Synchronize time')), 0, wx.EXPAND),
            (self.editsync, 0, wx.EXPAND),

            (wx.StaticText(self, -1, _('Lock device')), 0, wx.EXPAND),
            (self.editlock, 0, wx.EXPAND),

            (wx.StaticText(self, -1, _('Startup information')), 0, wx.EXPAND),
            (self.editinfo, 0, wx.EXPAND),

            (wx.StaticText(self, -1, _('Show debug log')), 0, wx.EXPAND),
            (self.editdebug, 0, wx.EXPAND),

            (wx.StaticText(self, -1, _('Automatically connect to phone on startup')), 0, wx.EXPAND),
            (self.editauto, 0, wx.EXPAND),

            (wx.StaticText(self, -1, _('Scale of SMS/EMS images')), 0, wx.EXPAND),
            (self.editscale, 0, wx.EXPAND),

            (wx.Button(self, wx.ID_OK, _('OK')), 0, wx.EXPAND),
            (wx.Button(self, wx.ID_CANCEL, _('Cancel')),  0, wx.EXPAND),
            ])
        self.sizer.Fit(self)
        self.SetAutoLayout(True)
        self.SetSizer(self.sizer)
        wx.EVT_BUTTON(self, wx.ID_OK, self.Okay)

    def Okay(self, evt):       
        self.config.Write('/Gammu/Model', self.editmodel.GetValue())
        self.config.Write('/Gammu/Device', self.editdev.GetValue())
        self.config.Write('/Gammu/Connection', self.editconn.GetValue())
        self.config.Write('/Gammu/SyncTime', self.editsync.GetValue())
        self.config.Write('/Gammu/LockDevice', self.editlock.GetValue())
        self.config.Write('/Gammu/StartInfo', self.editinfo.GetValue())
        self.config.Write('/Debug/Show', self.editdebug.GetValue())
        self.config.Write('/Wammu/AutoConnect', self.editauto.GetValue())
        self.config.WriteInt('/Wammu/ScaleImage', self.editscale.GetValue())
        self.EndModal(wx.ID_OK)
