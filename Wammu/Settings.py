import wx
import Wammu

class Settings(wx.Dialog): 
    def __init__(self, parent, config):
        wx.Dialog.__init__(self, parent, -1, _('Settings'), style = wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)
        self.sizer = wx.GridSizer(6, 2, 5, 5)  # rows, cols, hgap, vgap
        
        self.config = config
      
        if config['Model'] == None:
            config['Model'] = Wammu.Models[0]
     
        if config['Connection'] == None:
            config['Connection'] = Wammu.Connections[0]
      
        if config['Device'] == None:
            config['Device'] = Wammu.Devices[0]
       
        if config['SyncTime'] == 'yes':
            sync = 0
        else:
            sync = 1

        if config['LockDevice'] == 'yes':
            lock = 0
        else:
            lock = 1

        self.editdev = wx.ComboBox(self, -1, config['Device'], choices = Wammu.Devices)
        self.editconn = wx.ComboBox(self, -1, config['Connection'], choices = Wammu.Connections)
        self.editmodel = wx.ComboBox(self, -1, config['Model'], choices = Wammu.Models)
        self.editsync = wx.Choice(self, -1, (0,0), (0,0), [_('Yes'), _('No')])
        self.editsync.SetSelection(sync)
        self.editlock = wx.Choice(self, -1, (0,0), (0,0), [_('Yes'), _('No')])
        self.editlock.SetSelection(lock)

        self.sizer.AddMany([ 
            (wx.StaticText(self, -1, _('Device')), 0, wx.EXPAND),
            (self.editdev, 0, wx.EXPAND),

            (wx.StaticText(self, -1, _('Connection')), 0, wx.EXPAND),
            (self.editconn, 0, wx.EXPAND),

            (wx.StaticText(self, -1, _('Model')), 0, wx.EXPAND),
            (self.editmodel, 0, wx.EXPAND),

            (wx.StaticText(self, -1, _('Synchronize time')), 0, wx.EXPAND),
            (self.editsync, 0, wx.EXPAND),

            (wx.StaticText(self, -1, _('Lock device')), 0, wx.EXPAND),
            (self.editlock, 0, wx.EXPAND),


            (wx.Button(self, 1001, _('OK')), 0, wx.EXPAND),
            (wx.Button(self, 1002, _('Cancel')),  0, wx.EXPAND),
            ])
        self.sizer.Fit(self)
        self.SetAutoLayout(True)
        self.SetSizer(self.sizer)

