#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# vim: expandtab sw=4 ts=4 sts=4:
'''
Wammu - Phone manager
Execution script for configuration
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
import sys
import getopt
import wx
import re
import time
import Wammu
import Wammu.GammuSettings

# Try to import iconv_codec to allow working on chinese windows
try:
    import iconv_codec
except:
    pass

gettext.install('wammu', unicode=1)

def version():
    print _('Wammu Configurator - Wammu and Gammu configurator version %s') % Wammu.__version__

def usage():
    version()
    print _('Usage: %s [OPTION...]' % os.path.basename(__file__))
    print
    print _('Options:')
    print _('-h/--help          ... show this help')
    print _('-v/--version       ... show program version')
    print _('-l/--local-locales ... use locales from current directory rather than system ones')
    print

try:
    opts, args = getopt.getopt(sys.argv[1:], 'hvl', ['help', 'version', 'local-locales'])
except getopt.GetoptError, val:
    usage()
    print _('Command line parsing failed with error:')
    print val
    sys.exit(2)

if len(args) != 0:
    usage()
    print _('Extra unrecognized parameters passed to program')
    sys.exit(3)

for o, a in opts:
    if o in ('-l', '--local-locales'):
        gettext.install('wammu',os.path.join('build', 'share', 'locale'), unicode=1)
        print _('Using local built locales!')
    if o in ('-h', '--help'):
        usage()
        sys.exit()
    if o in ('-v', '--version'):
        version()
        sys.exit()

# need to be imported after locales are initialised
import Wammu.PhoneWizard
app = Wammu.PhoneWizard.WizardApp()

wammu_cfg = wx.Config(appName = 'Wammu', style = wx.CONFIG_USE_LOCAL_FILE)

config = Wammu.GammuSettings.GammuSettings(wammu_cfg)

position = config.SelectConfig(new = True)

if position is None:
    sys.exit()

result = Wammu.PhoneWizard.RunConfigureWizard(None, position)
if result is not None:
    busy = wx.BusyInfo(_('Updating gammu configuration...'))
    time.sleep(0.1)
    wx.Yield()
    config.SetConfig(result['Position'], result['Device'], result['Connection'], result['Name'])
app.Destroy()

