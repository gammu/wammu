# -*- coding: UTF-8 -*-
# vim: expandtab sw=4 ts=4 sts=4:
'''
Wammu - Phone manager
Unexpected exception handler
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

import traceback
import md5
from Wammu.Utils import Str_ as _
import Wammu.ErrorLog
import Wammu.ErrorMessage

# set later in Wammu.App to have correct parent here
handlerparent = None

def Handler(type, value, tback):
    """User friendly error handling """

    # prepare traceback text
    trace = traceback.extract_tb(tback)
    linetrace = traceback.format_list(trace)
    texttrace = ''.join(linetrace)
    textexc = ''.join(traceback.format_exception_only(type, value))

    # debug log information
    logtext = ''
    outf, logname = Wammu.ErrorLog.SaveLog()
    if outf is not None:
        print 'Created debug log copy in %s for error reporting.' % logname
        logtext =  '\n%s\n' % _('Debug log was saved for phone communication, if this error appeared during communicating with phone, you are strongly encouraged to include it in bugreport. Debug log is saved in file %s.') % logname

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
    if type == UnicodeEncodeError or type == UnicodeDecodeError:
        unicodewarning =  '\n%s\n' % _('Unicode encoding error appeared, see question 1 in FAQ, how to solve this.')
    else:
        unicodewarning = ''

    # prepare message
    text = """%s

%s
%s%s%s
%s
------------------ Traceback ID -------------------
%s
-------------------- Traceback --------------------
%s-------------------- Exception --------------------
%s---------------------------------------------------
""" % (
    _('Unhandled exception appeared.'),
    _('If you want to help improving this program, please submit following infomation and description how did it happen to %s. Please report in english, otherwise you will be most likely told to translate you report to english later.') % 'http://bugs.cihar.com',
    logtext, tracetext, unicodewarning, Wammu.ErrorLog.GetSystemInfo(), traceid, texttrace, textexc)

    # Include exception info in crash file
    if outf is not None:
        outf.write(text.encode('utf-8'))
        outf.close()

    # display error
    try:
        Wammu.ErrorMessage.ErrorMessage(handlerparent,
            _('Unhandled exception appeared. If you want to help improving this program, please report this together with description how this situation has happened. Please report in english, otherwise you will be most likely told to translate you report to english later.'),
            _('Unhandled exception'),
            traceid = traceid, autolog = logname,
            exception = _('Traceback:\n%(traceback)s\nException: %(exception)s') % { 'traceback': texttrace, 'exception' : textexc }).ShowModal()
    except:
        print text
