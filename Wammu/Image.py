# -*- coding: UTF-8 -*-
'''
Wammu - Phone manager
Image displaying classes to be embdeded inside wxHTML
'''
__author__ = 'Michal Čihař'
__email__ = 'michal@cihar.com'
__license__ = '''
Copyright (c) 2003 - 2006 Michal Čihař

This program is free software; you can redistribute it and/or modify it
under the terms of the GNU General Public License version 2 as published by
the Free Software Foundation.

This program is distributed in the hope that it will be useful, but WITHOUT
ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for
more details.

You should have received a copy of the GNU General Public License along with
this program; if not, write to the Free Software Foundation, Inc.,
51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
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
