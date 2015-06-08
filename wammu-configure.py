#!/usr/bin/env python
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
Execution script for configuration
'''

import os
import sys
import getopt
import wx
import time
import Wammu
import Wammu.GammuSettings
import Wammu.Locales
from Wammu.Locales import ugettext as _


def version():
    '''
    Displays version information.
    '''
    print (_('Wammu Configurator - Wammu and Gammu configurator version %s')
           % Wammu.__version__)


def usage():
    '''
    Shows program usage.
    '''
    version()
    print _('Usage: %s [OPTION...]' % os.path.basename(__file__))
    print
    print _('Options:')
    print '%-20s ... %s' % (
        '-h/--help',
        _('show this help')
    )
    print '%-20s ... %s' % (
        '-v/--version',
        _('show program version')
    )
    print '%-20s ... %s' % (
        '-l/--local-locales',
        _('force using of locales from current directory rather than system ones')
    )
    print


def parse_options():
    '''
    Processes program options.
    '''
    try:
        opts, args = getopt.getopt(
            sys.argv[1:],
            'hvl',
            ['help', 'version', 'local-locales']
        )
    except getopt.GetoptError, val:
        usage()
        print _('Command line parsing failed with error:')
        print val
        sys.exit(2)

    if len(args) != 0:
        usage()
        print _('Extra unrecognized parameters passed to program')
        sys.exit(3)

    for opt, dummy in opts:
        if opt in ('-l', '--local-locales'):
            Wammu.Locales.UseLocal()
            print _('Using local built locales!')
        if opt in ('-h', '--help'):
            usage()
            sys.exit()
        if opt in ('-v', '--version'):
            version()
            sys.exit()


def do_wizard():
    '''
    Runs configuration wizard.
    '''
    app = Wammu.PhoneWizard.WizardApp()

    wammu_cfg = Wammu.WammuSettings.WammuConfig()

    config = Wammu.GammuSettings.GammuSettings(wammu_cfg)

    position = config.SelectConfig(new=True)

    if position is None:
        sys.exit()

    result = Wammu.PhoneWizard.RunConfigureWizard(None, position)
    if result is not None:
        busy = wx.BusyInfo(_('Updating gammu configuration...'))
        time.sleep(0.1)
        wx.Yield()
        config.SetConfig(
            result['Position'],
            result['Device'],
            result['Connection'],
            result['Name']
        )
        del busy
    app.Destroy()


if __name__ == '__main__':
    Wammu.Locales.Init()
    parse_options()
    # need to be imported after locales are initialised
    import Wammu.PhoneWizard
    import Wammu.WammuSettings
    do_wizard()
