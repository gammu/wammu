import wx

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

class StaticBitmap(wx.StaticBitmap):
    def __init__(self, parent, image = defaultbmp, size = None, scale = 1):
        bitmap = wx.BitmapFromXPMData(image)
        if scale > 1:
            img = wx.ImageFromBitmap(bitmap)
            bitmap = wx.BitmapFromImage(img.Scale(bitmap.GetWidth() * scale, bitmap.GetHeight() * scale))
        wx.StaticBitmap.__init__(self, parent, -1, bitmap, (0,0))
