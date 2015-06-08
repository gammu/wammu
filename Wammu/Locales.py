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
Locales initialisation and gettext wrapper
'''

import os
import gettext
import locale
import codecs
import sys

_TRANSLATION = None


LOCAL_LOCALE_PATH = os.path.join('build', 'share', 'locale')
LOCALE_PATH = None

FALLBACK_LOCALE_CHARSET = 'iso-8859-1'

# Determine "correct" character set
try:
    # works only in python > 2.3
    LOCALE_CHARSET = locale.getpreferredencoding()
except:
    try:
        LOCALE_CHARSET = locale.getdefaultlocale()[1]
    except:
        try:
            LOCALE_CHARSET = sys.getdefaultencoding()
        except:
            LOCALE_CHARSET = FALLBACK_LOCALE_CHARSET
if LOCALE_CHARSET in [None, 'ANSI_X3.4-1968']:
    LOCALE_CHARSET = FALLBACK_LOCALE_CHARSET

try:
    CONSOLE_CHARSET = sys.stdout.encoding
except AttributeError:
    CONSOLE_CHARSET = None
if CONSOLE_CHARSET is None:
    CONSOLE_CHARSET = LOCALE_CHARSET
CONSOLE_ENCODER = codecs.getencoder(CONSOLE_CHARSET)

def ConsoleStrConv(txt):
    """
    This function coverts something (txt) to string form usable on console.
    """
    try:
        if isinstance(txt, str):
            return txt
        elif isinstance(txt, unicode):
            return str(CONSOLE_ENCODER(txt, 'replace')[0])
        return str(txt)
    except UnicodeEncodeError:
        return '???'

def StrConv(txt):
    """
    This function coverts something (txt) to string form usable by wxPython. There
    is problem that in default configuration in most distros (maybe all) default
    encoding for unicode objects is ascii. This leads to exception when converting
    something different than ascii. And this exception is not catched inside
    wxPython and leads to segfault.

    So if wxPython supports unicode, we give it unicode, otherwise locale
    dependant text.
    """
    try:
        if isinstance(txt, unicode):
            return txt
        elif isinstance(txt, str):
            return unicode(txt, LOCALE_CHARSET)
        return str(txt)
    except UnicodeEncodeError:
        return '???'

# detect html charset
HTML_CHARSET = LOCALE_CHARSET

# prepare html encoder
HTML_ENCODER = codecs.getencoder(HTML_CHARSET)

def HtmlStrConv(txt):
    """
    This function coverts something (txt) to string form usable by wxPython
    html widget. There is problem that in default configuration in most distros
    (maybe all) default encoding for unicode objects is ascii. This leads to
    exception when converting something different than ascii. And this
    exception is not catched inside wxPython and leads to segfault.

    So if wxPython supports unicode, we give it unicode, otherwise locale
    dependant text.
    """
    try:
        if isinstance(txt, unicode):
            return txt
        elif isinstance(txt, str):
            return unicode(txt, LOCALE_CHARSET)
        return str(txt)
    except UnicodeEncodeError:
        return '???'

def UnicodeConv(txt):
    """
    This function coverts something (txt) to string form usable by wxPython. There
    is problem that in default configuration in most distros (maybe all) default
    encoding for unicode objects is ascii. This leads to exception when converting
    something different than ascii. And this exception is not catched inside
    wxPython and leads to segfault.

    So if wxPython supports unicode, we give it unicode, otherwise locale
    dependant text.
    """
    try:
        if isinstance(txt, unicode):
            return txt
        elif isinstance(txt, str):
            return unicode(txt, LOCALE_CHARSET)
        return unicode(str(txt), LOCALE_CHARSET)
    except UnicodeEncodeError:
        return unicode('???')


def Init():
    '''
    Initialises gettext for wammu domain and installs global function _,
    which handles translations.
    '''
    global LOCALE_PATH
    switch = False
    if (os.path.exists('setup.py') and
        os.path.exists(LOCAL_LOCALE_PATH) and
        os.path.exists(
            os.path.join('Wammu', '__init__.py')
            )):
        LOCALE_PATH = LOCAL_LOCALE_PATH
        switch = True
    Install()
    if switch:
        print ConsoleStrConv(ugettext('Automatically switched to local locales.'))


def UseLocal():
    '''
    Use locales from current build dir.
    '''
    global LOCALE_PATH
    LOCALE_PATH = LOCAL_LOCALE_PATH
    Install()


def ngettext(msgid1, msgid2, n):
    if _TRANSLATION:
        return _TRANSLATION.ungettext(msgid1, msgid2, n)
    if n == 1:
        return msgid1
    else:
        return msgid2


def ugettext(message):
    if _TRANSLATION:
        return _TRANSLATION.ugettext(message)
    return message


def Install():
    global _TRANSLATION
    try:
        _TRANSLATION = gettext.translation(
            'wammu',
            localedir=LOCALE_PATH
        )
    except IOError:
        print ConsoleStrConv('Failed to load translation!')
