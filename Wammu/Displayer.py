import wx.html
import Wammu.Events

class Displayer(wx.html.HtmlWindow):
    def __init__(self, parent, win):
        wx.html.HtmlWindow.__init__(self, parent, -1)
        self.win = win

    def OnLinkClicked(self, linkinfo):
        evt = Wammu.Events.LinkEvent(
            link = linkinfo.GetHref()
            )
        wx.PostEvent(self.win, evt)

        
