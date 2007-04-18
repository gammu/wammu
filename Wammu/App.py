# -*- coding: ISO-8859-2 -*-
import wx

import Wammu.Main

class WammuApp(wx.App):

    # wxWindows calls this method to initialize the application
    def OnInit(self):

        self.SetAppName('Wammu')
        self.SetVendorName('Michal Čihař')

        wx.InitAllImageHandlers()
        frame = Wammu.Main.WammuFrame(None, -1)
        frame.Show(True)

        # Tell wxWindows that this is our main window
        self.SetTopWindow(frame)

        frame.PostInit()

        # Return a success flag
        return True

def Run():
    app = WammuApp()
    app.MainLoop()

