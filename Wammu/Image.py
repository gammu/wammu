# Wammu - Phone manager
# Copyright (c) 2003 - 2004 Michal Cihar 
#
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 2 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for
# more details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc., 59 Temple
# Place, Suite 330, Boston, MA 02111-1307 USA
'''
Image displaying classes to be embdeded inside wxHTML
'''

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
    def __init__(self, parent, tooltip = 'Image', image = defaultbmp, size = None, scale = 1):
        bitmap = wx.BitmapFromXPMData(image)
        if scale > 1:
            img = wx.ImageFromBitmap(bitmap)
            bitmap = wx.BitmapFromImage(img.Scale(bitmap.GetWidth() * scale, bitmap.GetHeight() * scale))
        wx.StaticBitmap.__init__(self, parent, -1, bitmap, (0,0))
        self.SetToolTipString(tooltip)

class Throbber(wx.lib.throbber.Throbber):
    def __init__(self, parent, tooltip = 'Animation', images = [defaultbmp], size = None, scale = 1, delay = 0.1):
        bitmaps = []
        for im in images:
            bitmap = wx.BitmapFromXPMData(im)
            if scale > 1:
                img = wx.ImageFromBitmap(bitmap)
                bitmap = wx.BitmapFromImage(img.Scale(bitmap.GetWidth() * scale, bitmap.GetHeight() * scale))
            bitmaps.append(bitmap) 
        wx.lib.throbber.Throbber.__init__(self, parent, -1, bitmaps, frameDelay = delay)
        self.SetToolTipString(tooltip)
