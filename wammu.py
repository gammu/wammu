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
Execution script
'''

import os
import sys
import getopt
import Wammu
import Wammu.Locales
from Wammu.Locales import ugettext as _

# Disable warning about missing files
# This can be caused by attempt to import Python modules, which don't
# have all DLLs satisfied.
if sys.platform.startswith('win'):
    import win32api
    import win32con
    win32api.SetErrorMode(win32con.SEM_NOOPENFILEERRORBOX)


def version():
    '''
    Displays version information.
    '''
    print _('Wammu - Windowed Gammu version %s') % Wammu.__version__


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
    print '%-20s ... %s' % (
        '-i/--info',
        _('prints connection settings and tries to connect the phone')
    )
    print '%-20s ... %s' % (
        '-d/--debug',
        _('enables debug output to stderr')
    )
    print


def info():
    '''
    Displays configuration summary and tries to connect to phone.
    '''
    import Wammu.WammuSettings
    import Wammu.Utils
    import gammu

    settings = Wammu.WammuSettings.WammuConfig()
    section = settings.ReadInt('/Gammu/Section')
    config = settings.gammu.GetConfig(section)
    if config['Connection'] == '' or config['Device'] == '':
        print _('Wammu is not configured!')

    cfg = {
        'StartInfo': settings.ReadBool('/Gammu/StartInfo'),
        'UseGlobalDebugFile': True,
        'DebugFile': None,  # Set on other place
        'SyncTime': settings.ReadBool('/Gammu/SyncTime'),
        'Connection': config['Connection'],
        'LockDevice': settings.ReadBool('/Gammu/LockDevice'),
        'DebugLevel': 'textalldate',  # Set on other place
        'Device': config['Device'],
        'Model': config['Model'],
    }

    # Compatibility with old Gammu versions
    cfg = Wammu.Utils.CompatConfig(cfg)

    print _('Wammu configuration:')
    print '%-15s: %s' % (_('Connection'), cfg['Connection'])
    print '%-15s: %s' % (_('Model'), cfg['Model'])
    print '%-15s: %s' % (_('Device'), cfg['Device'])
    print _('Connecting...')
    if Wammu.debug:
        gammu.SetDebugFile(sys.stderr)
        gammu.SetDebugLevel('textalldate')
    sm = gammu.StateMachine()
    sm.SetConfig(0, cfg)
    sm.Init()
    print _('Getting phone information...')
    Manufacturer = sm.GetManufacturer()
    Model = sm.GetModel()
    IMEI = sm.GetIMEI()
    Firmware = sm.GetFirmware()
    Code = sm.GetSecurityStatus()
    print _('Phone infomation:')
    print '%-15s: %s' % (_('Manufacturer'), Manufacturer)
    print '%-15s: %s (%s)' % (_('Model'), Model[0], Model[1])
    print '%-15s: %s' % (_('IMEI'), IMEI)
    print '%-15s: %s' % (_('Firmware'), Firmware[0])
    if Code is not None:
        print '%-15s: %s' % (_('Requested code'), Code)


def parse_options():
    '''
    Processes program options.
    '''
    try:
        opts, args = getopt.getopt(
            sys.argv[1:],
            'hvlid',
            ['help', 'version', 'local-locales', 'info', 'debug']
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

    do_info = False

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
        if opt in ('-i', '--info'):
            do_info = True
        if opt in ('-d', '--debug'):
            Wammu.debug = True

    if do_info:
        info()
        sys.exit()


if __name__ == '__main__':
    Wammu.Locales.Init()
    parse_options()
    # need to be imported after locales are initialised
    import Wammu.App
    Wammu.App.Run()
