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
Error log handling
'''

import Wammu
import tempfile
import wx
import sys
import os
import locale
if Wammu.gammu_error is None:
    import gammu

# set later in Wammu.Main to have correct debug filename
DEBUG_LOG_FILENAME = None

# Template for system information
SYSTEM_TEMPLATE = """
--------------- System information ----------------
Platform     %s
Python       %s
wxPython     %s
Wammu        %s
python-gammu %s
Gammu        %s
Bluetooth    %s
locales      %s (%s)
"""

def GetSystemInfo():
    """
    Returns system information in text form.
    """
    pyver = sys.version.split()[0]
    wxver = wx.VERSION_STRING
    wammuver = Wammu.__version__
    try:
        gammuver, pgammuver = gammu.Version()
    except:
        try:
            gammuver, pgammuver, ignore = gammu.Version()
        except:
            gammuver, pgammuver = ('Unknown', 'Unknown')
    loc, charset = locale.getdefaultlocale()
    bluez = 'None'
    try:
        import bluetooth
        bluez = 'PyBluez'
    except ImportError:
        pass

    result = SYSTEM_TEMPLATE % (
        sys.platform,
        pyver,
        wxver,
        wammuver,
        pgammuver,
        gammuver,
        bluez,
        loc,
        charset)

    if Wammu.configuration is not None:
        section = Wammu.configuration.ReadInt('/Gammu/Section')
        config = Wammu.configuration.gammu.GetConfig(section)
        result += 'connection   %s\n' % config['Connection']
        result += 'device       %s\n' % config['Device']
        result += 'model        %s\n' % config['Model']
    return result

def SaveLog(outf=None, filename=None):
    """
    Saves debug log to filename or handle. If none specified
    """
    if DEBUG_LOG_FILENAME is None:
        return None, None
    if outf is None:
        if filename is None:
            handle, name = tempfile.mkstemp('.log', 'wammu-crash-')
            outf = os.fdopen(handle, 'w+')
        else:
            name = filename
            outf = open(filename, 'w+')

    inf = open(DEBUG_LOG_FILENAME, 'r')
    outf.write(GetSystemInfo())
    outf.write(inf.read())
    inf.close()
    if filename is not None:
        outf.close()
    return outf, name
