# -*- coding: ISO-8859-2 -*-

import wx
import wx.html
import wx.lib.wxpTag
import sys
import gammu
import Wammu

if wx.USE_UNICODE:
    text = '''
<html>
<body>
<center><table width="100%%" cellspacing="0"
cellpadding="0" border="1">
<tr>
    <td align="center">
    <h1>Wammu %s</h1>
    Running on Python %s<br>
    Using wxPython %s<br>
    Using python-gammu %s and Gammu %s<br>
    </td>
</tr>
</table>

<p><b>Wammu</b> is a wxPython based GUI for Gammu.</p>

<p>
<font size=-3>
Copyright &copy; 2003-2004 Michal &#268;iha&#345;
<br><br>

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.
<br><br>

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.
</font>
</p>

<p><wxp module="wx" class="Button">
    <param name="label" value="Ok">
    <param name="id"    value="ID_OK">
</wxp></p>
</center>
</body>
</html>
'''
else:
    text = '''
<html>
<head><meta http-equiv="Content-Type" content="text/html; charset=iso-8859-2"></head>
<body>
<center><table width="100%%" cellspacing="0"
cellpadding="0" border="1">
<tr>
    <td align="center">
    <h1>Wammu %s</h1>
    Running on Python %s<br>
    Using wxPython %s<br>
    Using python-gammu %s and Gammu %s<br>
    </td>
</tr>
</table>

<p><b>Wammu</b> is a wxPython based GUI for Gammu.</p>

<p>
<font size=-3>
Copyright (c) 2003-2004 Michal Čihař
<br><br>

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.
<br><br>

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.
</font>
</p>

<p><wxp module="wx" class="Button">
    <param name="label" value="Ok">
    <param name="id"    value="ID_OK">
</wxp></p>
</center>
</body>
</html>
'''

class AboutBox(wx.Dialog):
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, -1, 'About Wammu',)
        html = wx.html.HtmlWindow(self, -1, size=(420, -1))
        py_version = sys.version.split()[0]
        html.SetPage(text % (Wammu.__version__, py_version, wx.VERSION_STRING, gammu.Version()[1], gammu.Version()[0]))
        btn = html.FindWindowById(wx.ID_OK)
        btn.SetDefault()
        ir = html.GetInternalRepresentation()
        html.SetSize( (ir.GetWidth()+25, ir.GetHeight()+25) )
        self.SetClientSize(html.GetSize())
        self.CentreOnParent(wx.BOTH)

