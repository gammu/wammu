# -*- coding: UTF-8 -*-
'''
Wammu - Phone manager
About dialog
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
import wx.html
import wx.lib.wxpTag
import sys
import Wammu
if Wammu.gammu_error == None:
    import gammu
import Wammu.Utils
from Wammu.Paths import *
from Wammu.Utils import HtmlStr_ as _, HtmlStrConv

class AboutBox(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, -1, _('About Wammu'))

        if wx.USE_UNICODE:
            copyrightline = u'Copyright &copy; 2003 - 2006 Michal Čihař'
            head = ''
        else:
            copyrightline = HtmlStrConv(u'Copyright (c) 2003 - 2006 Michal Čihař')
            if copyrightline.find('?') != -1:
                copyrightline = 'Copyright (c) 2003 - 2006 Michal Cihar'
            head = '<head><meta http-equiv="Content-Type" content="text/html; charset=%s"></head>' % Wammu.Utils.htmlcharset

        # default system colours
        bgc = wx.SystemSettings.GetColour(wx.SYS_COLOUR_BTNFACE)
        fgc = wx.SystemSettings.GetColour(wx.SYS_COLOUR_BTNTEXT)
        hfgc = wx.SystemSettings.GetColour(wx.SYS_COLOUR_BTNHIGHLIGHT)

        colours = 'text="#%02x%02x%02x" bgcolor="#%02x%02x%02x" link="#%02x%02x%02x"' % (
            fgc.Red(), fgc.Green(), fgc.Blue(),
            bgc.Red(), bgc.Green(), bgc.Blue(),
            hfgc.Red(), hfgc.Green(), hfgc.Blue())

        text = '''
<html>
%s
<body %s>
<center><font color="#ffffff"><table bgcolor="#458154" width="100%%" cellspacing="0"
cellpadding="0" border="1">
<tr>
    <td align="center">
    %s
    </td>
</tr>
</table></font>

<p>%s</p>

<p>
<font size=-3>
%s
<br><br>
%s
<br><br>
%s
</font>
</p>
<p>
<wxp module="wx" class="Button">
    <param name="label" value="%s">
    <param name="id"    value="ID_OK">
</wxp>
</p>
</center>
</body>
</html>

''' % (head, colours, '''<img src="%s"><br><h2> Wammu %s</h2>
    %s<br>
    %s<br>
    %s<br>
''' % (AppIconPath('wammu'),
            Wammu.__version__,
            _('Running on Python %s') % sys.version.split()[0],
            _('Using wxPython %s') % wx.VERSION_STRING,
            _('Using python-gammu %(python_gammu_version)s and Gammu %(gammu_version)s') %
                {
                    'python_gammu_version':gammu.Version()[1],
                    'gammu_version': gammu.Version()[0]
                }),
            _('<b>Wammu</b> is a wxPython based GUI for Gammu.'),
            copyrightline,
            _('''
This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License version 2 as
published by the Free Software Foundation.
'''),
            _('''
This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.
'''),
            _('OK'))

        html = wx.html.HtmlWindow(self, -1, size = (500, -1))
        html.SetPage(text)
        btn = html.FindWindowById(wx.ID_OK)
        if btn != None:
            btn.SetDefault()
        ir = html.GetInternalRepresentation()
        html.SetSize( (ir.GetWidth()+25, ir.GetHeight()+25) )
        self.SetClientSize(html.GetSize())
        self.CentreOnParent(wx.BOTH)
