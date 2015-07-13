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
Unexpected exception handler
'''

import traceback
try:
    from hashlib import md5 as md5
except ImportError:
    from md5 import new as md5
import Wammu.ErrorLog
import Wammu.ErrorMessage
from Wammu.Locales import StrConv
from Wammu.Locales import ugettext as _

# set later in Wammu.App to have correct parent here
HANDLER_PARENT = None

ERROR_HISTORY = []

def Handler(errtype, value, tback):
    """User friendly error handling """

    # prepare traceback text
    trace = traceback.extract_tb(tback)
    linetrace = traceback.format_list(trace)
    texttrace = ''.join(linetrace)
    textexc = ''.join(traceback.format_exception_only(errtype, value))

    # debug log information
    logtext = ''
    outf, logname = Wammu.ErrorLog.SaveLog()
    if outf is not None:
        print 'Created debug log copy in %s for error reporting.' % logname
        logtext = '\n%s\n' % _('Debug log was saved for phone communication, if this error appeared during communicating with phone, you are strongly encouraged to include it in bugreport. Debug log is saved in file %s.') % logname


    # detection of same errors
    tracehash = md5('%s,%s' % (textexc, texttrace)).hexdigest()
    if tracehash in ERROR_HISTORY:
        print 'Same error already detected, not showing dialog!'
        print texttrace
        print 'Exception: %s' % textexc
        return
    ERROR_HISTORY.append(tracehash)

    # traceback id (md5 sum of last topmost traceback item inside Wammu - file(function):code)
    try:
        for trace_line in trace:
            if trace_line[0].rfind('Wammu') > -1:
                lasttrace = trace_line
        traceidtext = '%s(%s):%s' % (
                lasttrace[0][lasttrace[0].rfind('Wammu'):],
                lasttrace[2],
                lasttrace[3])
        traceid = md5(traceidtext).hexdigest()
        tracetext = '\n%s\n' % (
                _('Before submiting please try searching for simmilar bugs on %s')
                % ('https://github.com/search?l=&q=%s+%%40gammu&ref=advsearch&type=Issues'
                    % traceid))
    except:
        traceid = 'N/A'
        tracetext = ''

    # unicode warning
    if errtype == UnicodeEncodeError or errtype == UnicodeDecodeError:
        unicodewarning = '\n%s\n' % (
            _('Unicode encoding error appeared, see question 1 in FAQ, how to solve this.')
        )
    else:
        unicodewarning = ''

    # prepare message
    text = u"""%s

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
        _('If you want to help improving this program, please submit following infomation and description how did it happen to %s. Please report in english, otherwise you will be most likely told to translate you report to english later.') % 'http://bugs.wammu.eu/',
        logtext,
        tracetext,
        unicodewarning,
        Wammu.ErrorLog.GetSystemInfo(),
        traceid,
        StrConv(texttrace),
        StrConv(textexc)
    )

    # Include exception info in crash file
    if outf is not None:
        outf.write(text.encode('utf-8'))
        outf.close()

    # display error
    try:
        Wammu.ErrorMessage.ErrorMessage(
            HANDLER_PARENT,
            _('Unhandled exception appeared. If you want to help improving this program, please report this together with description how this situation has happened. Please report in english, otherwise you will be most likely told to translate you report to english later.'),
            _('Unhandled exception'),
            traceid=traceid,
            autolog=logname,
            exception=_('Traceback:\n%(traceback)s\nException: %(exception)s') % {
                'traceback': StrConv(texttrace),
                'exception': StrConv(textexc)
            }
        ).ShowModal()
    except:
        print text
