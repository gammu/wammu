# -*- coding: ISO-8859-2 -*-
import wx
import sys
import Wammu.Main
import Wammu.Error
from Wammu.Paths import *

class WammuApp(wx.App):

    # wxWindows calls this method to initialize the application
    def OnInit(self):

        self.SetAppName('Wammu')
        self.SetVendorName('Michal Čihař')

        wx.InitAllImageHandlers()
        #spl = wx.SplashScreen(wx.Bitmap(MiscPath('splash')), wx.SPLASH_CENTRE_ON_SCREEN | wx.SPLASH_TIMEOUT, 5000, None, -1)
        frame = Wammu.Main.WammuFrame(None, -1)

        frame.Show(True)
        frame.PostInit()
        self.SetTopWindow(frame)
        #spl.Destroy()


        # Return a success flag
        return True

def Run():
    try:
        sys.excepthook = Wammu.Error.Handler
    except:
        print _('Failed to set exception handler.')
    app = WammuApp()
    app.MainLoop()

