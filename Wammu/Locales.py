# -*- coding: UTF-8 -*-
# vim: expandtab sw=4 ts=4 sts=4:
'''
Wammu - Phone manager
Locales initialisation
'''
__author__ = 'Michal Čihař'
__email__ = 'michal@cihar.com'
__license__ = '''
Copyright (c) 2003 - 2007 Michal Čihař

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

import os
import gettext
import __builtin__

LOCALEPATH = os.path.join('build', 'share', 'locale')

def Init():
    '''
    Initialises gettext for wammu domain and installs global function _,
    which handles translations.
    '''
    gettext.textdomain('wammu')
    __builtin__.__dict__['_'] = gettext.gettext
    if (os.path.exists('setup.py') and
        os.path.exists(LOCALEPATH) and
        os.path.exists(
            os.path.join('Wammu', '__init__.py')
            )):
        UseLocal()
        print _('Automatically switched to local locales.')

def UseLocal():
    '''
    Use locales from current build dir.
    '''
    gettext.bindtextdomain('wammu', LOCALEPATH)
