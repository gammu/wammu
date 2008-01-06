#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# vim: expandtab sw=4 ts=4 sts=4:
'''
Wammu - Phone manager
Execution script
'''
__author__ = 'Michal Čihař'
__email__ = 'michal@cihar.com'
__license__ = '''
Copyright © 2003 - 2008 Michal Čihař

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
import sys
import getopt
import Wammu
import Wammu.Locales

# Try to import iconv_codec to allow working on chinese windows
try:
    import iconv_codec
except ImportError:
    pass

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
            _('show this help'))
    print '%-20s ... %s' % (
            '-v/--version',
            _('show program version'))
    print '%-20s ... %s' % (
            '-l/--local-locales',
            _('force using of locales from current directory rather than system ones'))
    print

def parse_options():
    '''
    Processes program options.
    '''
    try:
        opts, args = getopt.getopt(sys.argv[1:], 
                'hvl', 
                ['help', 'version', 'local-locales'])
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

if __name__ == '__main__':
    Wammu.Locales.Init()
    parse_options()
    # need to be imported after locales are initialised
    import Wammu.App
    Wammu.App.Run()
