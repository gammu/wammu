try:
    from wx.lib.newevent import NewEvent
except:
    print 'Please consider updating to newer wxPython, using local copy of newevent'
    from Wammu.wxcomp.newevent import NewEvent

# create some events:
ShowMessageEvent, EVT_SHOW_MESSAGE = NewEvent()
ProgressEvent, EVT_PROGRESS = NewEvent()
LinkEvent, EVT_LINK = NewEvent()
DataEvent, EVT_DATA = NewEvent()
ShowEvent, EVT_SHOW = NewEvent()
EditEvent, EVT_EDIT = NewEvent()
SendEvent, EVT_SEND = NewEvent()
ReplyEvent, EVT_REPLY = NewEvent()
DuplicateEvent, EVT_DUPLICATE = NewEvent()
DeleteEvent, EVT_DELETE = NewEvent()
LogEvent, EVT_LOG = NewEvent()
TextEvent, EVT_TEXT = NewEvent()
DoneEvent, EVT_DONE = NewEvent()
BackupEvent, EVT_BACKUP = NewEvent()

