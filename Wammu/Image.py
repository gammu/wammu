import wx
import wx.lib.throbber

defaultbmp = [
    '20 20 2 1', 
    '. c Black', 
    '  c None', 
    '                    ', 
    ' ..              .. ', 
    ' ...            ... ', 
    '  ...          ...  ', 
    '   ...        ...   ', 
    '    ...      ...    ', 
    '     ...    ...     ', 
    '      ...  ...      ', 
    '       ......       ', 
    '        ....        ', 
    '        ....        ', 
    '       ......       ', 
    '      ...  ...      ', 
    '     ...    ...     ', 
    '    ...      ...    ', 
    '   ...        ...   ', 
    '  ...          ...  ', 
    ' ...            ... ', 
    ' ..              .. ', 
    '                    ']

class Bitmap(wx.StaticBitmap):
    def __init__(self, parent, image = defaultbmp, size = None, scale = 1):
        bitmap = wx.BitmapFromXPMData(image)
        if scale > 1:
            img = wx.ImageFromBitmap(bitmap)
            bitmap = wx.BitmapFromImage(img.Scale(bitmap.GetWidth() * scale, bitmap.GetHeight() * scale))
        wx.StaticBitmap.__init__(self, parent, -1, bitmap, (0,0))

class Throbber(wx.lib.throbber.Throbber):
    def __init__(self, parent, images = [defaultbmp], size = None, scale = 1, delay = 0.1):
        bitmaps = []
        for im in images:
            bitmap = wx.BitmapFromXPMData(x)
            if scale > 1:
                img = wx.ImageFromBitmap(bitmap)
                bitmap = wx.BitmapFromImage(img.Scale(bitmap.GetWidth() * scale, bitmap.GetHeight() * scale))
            bitmaps.append(bitmap) 
        wx.lib.throbber.Throbber.__init__(self, parent, -1, bitmaps, frameDelay = delay)
