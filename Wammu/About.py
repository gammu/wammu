# -*- coding: UTF-8 -*-
# Wammu - Phone manager
# Copyright (c) 2003 - 2005 Michal Čihař
#
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 2 of the License.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for
# more details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc., 59 Temple
# Place, Suite 330, Boston, MA 02111-1307 USA
#
'''
About dialog
'''

import wx
import wx.html
import wx.lib.wxpTag
import sys
import gammu
import Wammu
import Wammu.Utils
from Wammu.Paths import *
from Wammu.Utils import HtmlStr_ as _, HtmlStrConv

if wx.USE_UNICODE:
    copyrightline = u'Copyright &copy; 2003 - 2005 Michal Čihař'
    head = ''
else:
    copyrightline = HtmlStrConv(u'Copyright (c) 2003 - 2005 Michal Čihař')
    if copyrightline.find('?') != -1:
        copyrightline = 'Copyright (c) 2003 - 2005 Michal Cihar'
    head = '<head><meta http-equiv="Content-Type" content="text/html; charset=%s"></head>' % Wammu.Utils.htmlcharset

text = '''
<html>
%s
<body>
<center><table bgcolor="#458154" width="100%%" cellspacing="0"
cellpadding="0" border="1">
<tr>
    <td align="center">
    %s
    </td>
</tr>
</table>

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

''' % (head, '''<img src="%s"><br><h2> Wammu %s</h2>
    %s<br>
    %s<br>
    %s<br>
''' % (AppIconPath('wammu'),
    Wammu.__version__,
    _('Running on Python %s') % sys.version.split()[0],
    _('Using wxPython %s') % wx.VERSION_STRING,
    _('Using python-gammu %s and Gammu %s') %  (gammu.Version()[1], gammu.Version()[0])),
    _('<b>Wammu</b> is a wxPython based GUI for Gammu.'),
    copyrightline,
    _('''
This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.
'''),
    _('''
This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.
'''),
    _('OK'))

class AboutBox(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, -1, _('About Wammu'))
        html = wx.html.HtmlWindow(self, -1, size = (500, -1))
        html.SetPage(text)
        btn = html.FindWindowById(wx.ID_OK)
        if btn != None:
            btn.SetDefault()
        ir = html.GetInternalRepresentation()
        html.SetSize( (ir.GetWidth()+25, ir.GetHeight()+25) )
        self.SetClientSize(html.GetSize())
        self.CentreOnParent(wx.BOTH)
