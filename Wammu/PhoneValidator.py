import wx
import re

validchars = '0123456789+#*'
matcher = re.compile('^\\+?[0-9*#]+$')
matcherp = re.compile('^\\+?[P0-9*#]+$')

class PhoneValidator(wx.PyValidator):
    def __init__(self, multi=False, pause=False, empty=False):
        wx.PyValidator.__init__(self)
        self.multi = multi
        self.pause = pause
        self.empty = empty
        wx.EVT_CHAR(self, self.OnChar)

    def Clone(self):
        return PhoneValidator(self.multi, self.pause, self.empty)

    def TransferToWindow(self):
        return True

    def TransferFromWindow(self):
        return True

    def CheckText(self, val, immediate = False):
        if val == '':
            result = self.empty
        elif immediate and val == '+':
            result = True
        else:
            if self.pause:
                if matcherp.match(val) == None:
                    result = False
                else:
                    result = True
            else:
                if matcher.match(val) == None:
                    result = False
                else:
                    result = True
        return result

    def Validate(self, win = None):
        tc = self.GetWindow()
        val = tc.GetValue()

        result = self.CheckText(val)

        if not result and win != None:
            wx.MessageDialog(win,
                _('You did not specify valid phone number.'),
                _('Invalid phone number'),
                wx.OK | wx.ICON_WARNING).ShowModal()
            tc.SetFocus()

        return result

    def OnChar(self, event):
        key = event.KeyCode()
        if key < wx.WXK_SPACE or key == wx.WXK_DELETE or key > 255:
            event.Skip()
            return

        tc = self.GetWindow()
        val = tc.GetValue()
        if self.CheckText(val + chr(key), immediate = True):
            event.Skip()
            return

        if not wx.Validator_IsSilent():
            wx.Bell()

        # Returning without calling even.Skip eats the event before it
        # gets to the text control
        return

