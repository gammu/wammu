# -*- coding: UTF-8 -*-
#
# Copyright © 2003 - 2015 Michal Čihař <michal@cihar.com>
#
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License version 2 as published by
# the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for
# more details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
#
# vim: expandtab sw=4 ts=4 sts=4:
'''
Wammu - Phone manager
About dialog
'''

import wx
import wx.html
import wx.lib.wxpTag
import sys
import Wammu
if Wammu.gammu_error is None:
    import gammu
import Wammu.Utils
import Wammu.Paths
from Wammu.Locales import ugettext as _

class AboutBox(wx.Dialog):
    '''
    Displays box showing information about program including versions of used
    components.
    '''
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, -1, _('About Wammu'))

        copyrightline = u'Copyright &copy; 2003 - 2011 Michal Čihař'

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
    <param name="id"    value="ID_OK">
</wxp>
</p>
</center>
</body>
</html>

''' % (colours, '''<img src="%s"><br><h2> Wammu %s</h2>
    %s<br>
    %s<br>
    %s<br>
''' % (Wammu.Paths.AppIconPath('wammu'),
            Wammu.__version__,
            _('Running on Python %s') % sys.version.split()[0],
            _('Using wxPython %s') % wx.VERSION_STRING,
            _('Using python-gammu %(python_gammu_version)s and Gammu %(gammu_version)s') % {
                'python_gammu_version': gammu.Version()[1],
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
'''))

        html = wx.html.HtmlWindow(self, -1, size=(500, -1))
        html.SetPage(text)
        btn = html.FindWindowById(wx.ID_OK)
        if btn is not None:
            btn.SetDefault()
        representation = html.GetInternalRepresentation()
        html.SetSize(
            (representation.GetWidth() + 25, representation.GetHeight() + 25)
        )
        self.SetClientSize(html.GetSize())
        self.CentreOnParent(wx.BOTH)
