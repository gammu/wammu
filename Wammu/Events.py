import wx.lib.newevent

# create some events:
ShowMessageEvent, EVT_SHOW_MESSAGE = wx.lib.newevent.NewEvent()
ProgressEvent, EVT_PROGRESS = wx.lib.newevent.NewEvent()
LinkEvent, EVT_LINK = wx.lib.newevent.NewEvent()
DataEvent, EVT_DATA = wx.lib.newevent.NewEvent()
ShowEvent, EVT_SHOW = wx.lib.newevent.NewEvent()
EditEvent, EVT_EDIT = wx.lib.newevent.NewEvent()
DuplicateEvent, EVT_DUPLICATE = wx.lib.newevent.NewEvent()
DeleteEvent, EVT_DELETE = wx.lib.newevent.NewEvent()
LogEvent, EVT_LOG = wx.lib.newevent.NewEvent()

