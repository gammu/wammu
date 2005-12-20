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
# this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
'''
Unexpected exception handler
'''

import Wammu
if Wammu.gammu_error == None:
    import gammu
import wx
import wx.lib.dialogs
import traceback
import sys
import locale
import md5
from Wammu.Utils import Str_ as _

# set later in Wammu.App to have correct parent here
handlerparent = None

def Handler(type, value, tback):
    """User friendly error handling """

    # first get some information
    pyver = sys.version.split()[0]
    wxver = wx.VERSION_STRING
    wammuver = Wammu.__version__
    (gammuver, pgammuver) = gammu.Version()
    (loc, charset) = locale.getdefaultlocale()

    # prepare traceback text
    trace = traceback.extract_tb(tback)
    linetrace = traceback.format_list(trace)
    texttrace = ''.join(linetrace)
    textexc = ''.join(traceback.format_exception_only(type, value))

    # traceback id (md5 sum of last topmost traceback item inside Wammu - file(function):code)
    try:
        for tr in trace:
            if tr[0].rfind('Wammu') > -1:
                lasttrace = tr
        traceidtext = '%s(%s):%s' % (lasttrace[0][lasttrace[0].rfind('Wammu'):], lasttrace[2], lasttrace[3])
        traceid = md5.new(traceidtext).hexdigest()
        tracetext = '\n%s\n' % (_('Before submiting please try searching for simmilar bugs on %s') % ('http://bugs.cihar.com/view_all_set.php?f=3&type=1&search=%s\n' % traceid))
    except:
        traceid = 'N/A'
        tracetext = ''

    # unicode warning
    if type == UnicodeEncodeError:
        unicodewarning =  '\n%s\n' % _('Unicode encoding error appeared, see question 1 in FAQ, how to solve this.')
    else:
        unicodewarning = ''

    # prepare message
    text = """%s

%s
%s%s
--------------- System information ----------------
Python       %s
wxPython     %s
Wammu        %s
python-gammu %s
Gammu        %s
locales      %s (%s)
------------------ Traceback ID -------------------
%s
-------------------- Traceback --------------------
%s-------------------- Exception --------------------
%s---------------------------------------------------
""" % (
    _('Unhandled exception appeared.'),
    _('If you want to help improving this program, please submit following infomation and description how did it happen to %s.') % 'http://bugs.cihar.com',
    tracetext, unicodewarning, pyver, wxver, wammuver, pgammuver, gammuver, loc, charset, traceid, texttrace, textexc)

    # display error
    try:
        wx.lib.dialogs.ScrolledMessageDialog(handlerparent, text, _('Unhandled exception')).ShowModal()
    except:
        print text
