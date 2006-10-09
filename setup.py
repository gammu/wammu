#!/usr/bin/env python
# -*- coding: UTF-8 -*-
'''
Wammu - Phone manager
Setup script for installation using distutils
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

from distutils.core import setup
from distutils.command.build_scripts import build_scripts
from distutils.util import convert_path
from distutils.dep_util import newer
from distutils import log
from distutils import sysconfig
from stat import ST_MODE
import sys
import glob
import Wammu
import os.path
import os
import re
# Optional support for py2exe
try:
    import py2exe
except:
    pass

# detect whether we should check for dependencies
skip_deps = 'clean' in sys.argv or '--help' in sys.argv or '--help-commands' in sys.argv or 'sdist' in sys.argv

# somw defines
PYTHONGAMMU_REQUIRED = (0,10)

if not skip_deps:
    if os.getenv('SKIPGAMMUCHECK') == 'yes':
        print 'Skipping Gammu check, expecting you know what you are doing!'
    else:
        try:
            import gammu
        except ImportError:
            print 'You need python-gammu!'
            print 'You can get it from <http://cihar.com/gammu/python/>'
            sys.exit(1)
        pygver = tuple(map(int, gammu.Version()[1].split('.')))
        if  pygver < PYTHONGAMMU_REQUIRED:
            print 'You need python-gammu at least %s!' % '.'.join(map(str, PYTHONGAMMU_REQUIRED))
            print 'You can get it from <http://cihar.com/gammu/python/>'
            sys.exit(1)

    if os.getenv('SKIPWXCHECK') == 'yes':
        print 'Skipping wx check, expecting you know what you are doing!'
    else:
        try:
            import wx
        except ImportError:
            print 'You need wxPython!'
            print 'You can get it from <http://www.wxpython.org>'
            sys.exit(1)
        if wx.VERSION < (2,6,0,0):
            print 'You need at least wxPython 2.6.0.0!'
            print 'You can get it from <http://www.wxpython.org>'
            sys.exit(1)

    try:
        import gnomebt.controller
    except ImportError:
        try:
            import bluetooth
        except ImportError:
            print 'WARNING: neither GNOME Bluetooth nor PyBluez found, without those you can not search for bluetooth devices'
            print 'GNOME Bluetooth can be downloaded from <http://usefulinc.com/software/gnome-bluetooth>'
            print 'PyBluez can be downloaded from <http://org.csail.mit.edu/pybluez/>'

# check if Python is called on the first line with this expression
first_line_re = re.compile('^#!.*python[0-9.]*([ \t].*)?$')

class build_scripts_wammu(build_scripts):
    '''
    This is mostly distutils copy, it just renames script according
    to platform (.pyw for Windows, without extension for others)
    '''
    def copy_scripts (self):
        """Copy each script listed in 'self.scripts'; if it's marked as a
        Python script in the Unix way (first line matches 'first_line_re',
        ie. starts with "\#!" and contains "python"), then adjust the first
        line to refer to the current Python interpreter as we copy.
        """
        self.mkpath(self.build_dir)
        outfiles = []
        for script in self.scripts:
            adjust = 0
            script = convert_path(script)
            outfile = os.path.join(self.build_dir, os.path.splitext(os.path.basename(script))[0])
            if sys.platform == 'win32':
                outfile += os.extsep + 'pyw'
            outfiles.append(outfile)

            if not self.force and not newer(script, outfile):
                log.debug("not copying %s (up-to-date)", script)
                continue

            # Always open the file, but ignore failures in dry-run mode --
            # that way, we'll get accurate feedback if we can read the
            # script.
            try:
                f = open(script, "r")
            except IOError:
                if not self.dry_run:
                    raise
                f = None
            else:
                first_line = f.readline()
                if not first_line:
                    self.warn("%s is an empty file (skipping)" % script)
                    continue

                match = first_line_re.match(first_line)
                if match:
                    adjust = 1
                    post_interp = match.group(1) or ''

            if adjust:
                log.info("copying and adjusting %s -> %s", script,
                         self.build_dir)
                if not self.dry_run:
                    outf = open(outfile, "w")
                    if not sysconfig.python_build:
                        outf.write("#!%s%s\n" %
                                   (os.path.normpath(sys.executable),
                                    post_interp))
                    else:
                        outf.write("#!%s%s\n" %
                                   (os.path.join(
                            sysconfig.get_config_var("BINDIR"),
                            "python" + sysconfig.get_config_var("EXE")),
                                    post_interp))
                    outf.writelines(f.readlines())
                    outf.close()
                if f:
                    f.close()
            else:
                f.close()
                self.copy_file(script, outfile)

        if os.name == 'posix':
            for file in outfiles:
                if self.dry_run:
                    log.info("changing mode of %s", file)
                else:
                    oldmode = os.stat(file)[ST_MODE] & 07777
                    newmode = (oldmode | 0555) & 07777
                    if newmode != oldmode:
                        log.info("changing mode of %s from %o to %o",
                                 file, oldmode, newmode)
                        os.chmod(file, newmode)

    # copy_scripts ()



setup(name="wammu",
    version = Wammu.__version__,
    description = "Wammu",
    long_description = "Phone manager built on top of python-gammu. Supports many phones.",
    author = "Michal Čihař",
    author_email = "michal@cihar.com",
    maintainer = "Michal Čihař",
    maintainer_email = "michal@cihar.com",
    url = "http://cihar.com/gammu/wammu",
    license = "GPL",
    classifiers = [
        'Development Status :: 5 - Production/Stable',
        'Environment :: Win32 (MS Windows)',
        'Environment :: X11 Applications :: GTK',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Operating System :: Microsoft :: Windows :: Windows 95/98/ME',
        'Operating System :: Microsoft :: Windows :: Windows NT/2000/XP',
        'Operating System :: POSIX',
        'Operating System :: Unix',
        'Programming Language :: Python',
        'Topic :: Communications :: Telephony',
        'Topic :: Office/Business :: Scheduling',
        'Topic :: Utilities',
        'Translations :: English',
        'Translations :: Catalan',
        'Translations :: Czech',
        'Translations :: Dutch',
        'Translations :: Estonian',
        'Translations :: Finnish',
        'Translations :: French',
        'Translations :: German',
        'Translations :: Hungarian',
        'Translations :: Italian',
        'Translations :: Korean',
        'Translations :: Polish',
        'Translations :: Portuguese (Brazil)',
        'Translations :: Slovak',
        'Translations :: Spanish',
        'Translations :: Swedish',
    ],
    packages = ['Wammu', 'Wammu.wxcomp'],
    scripts = ['wammu.py'],
    data_files = [
        (os.path.join('share','Wammu','images','icons'), glob.glob('images/icons/*.png')),
        (os.path.join('share','Wammu','images','misc'), glob.glob('images/misc/*.png')),
        (os.path.join('share','locale','ca','LC_MESSAGES'), ['locale/ca/LC_MESSAGES/wammu.mo']),
        (os.path.join('share','locale','cs','LC_MESSAGES'), ['locale/cs/LC_MESSAGES/wammu.mo']),
        (os.path.join('share','locale','de','LC_MESSAGES'), ['locale/de/LC_MESSAGES/wammu.mo']),
        (os.path.join('share','locale','es','LC_MESSAGES'), ['locale/es/LC_MESSAGES/wammu.mo']),
        (os.path.join('share','locale','et','LC_MESSAGES'), ['locale/et/LC_MESSAGES/wammu.mo']),
        (os.path.join('share','locale','fi','LC_MESSAGES'), ['locale/fi/LC_MESSAGES/wammu.mo']),
        (os.path.join('share','locale','fr','LC_MESSAGES'), ['locale/fr/LC_MESSAGES/wammu.mo']),
        (os.path.join('share','locale','hu','LC_MESSAGES'), ['locale/hu/LC_MESSAGES/wammu.mo']),
        (os.path.join('share','locale','ko','LC_MESSAGES'), ['locale/ko/LC_MESSAGES/wammu.mo']),
        (os.path.join('share','locale','nl','LC_MESSAGES'), ['locale/nl/LC_MESSAGES/wammu.mo']),
        (os.path.join('share','locale','it','LC_MESSAGES'), ['locale/it/LC_MESSAGES/wammu.mo']),
        (os.path.join('share','locale','pl','LC_MESSAGES'), ['locale/pl/LC_MESSAGES/wammu.mo']),
        (os.path.join('share','locale','pt_BR','LC_MESSAGES'), ['locale/pt_BR/LC_MESSAGES/wammu.mo']),
        (os.path.join('share','locale','sk','LC_MESSAGES'), ['locale/sk/LC_MESSAGES/wammu.mo']),
        (os.path.join('share','locale','sv','LC_MESSAGES'), ['locale/sv/LC_MESSAGES/wammu.mo']),
        (os.path.join('share','applications'), ['wammu.desktop']),
        (os.path.join('share','pixmaps'), ['icon/wammu.png', 'icon/wammu.xpm', 'icon/wammu.ico']),
        (os.path.join('share','man','man1'), ['wammu.1'])
        ],
    # Override certain command classes with our own ones
    cmdclass = {
        'build_scripts': build_scripts_wammu,
        },
    # py2exe options
    options = {'py2exe': {'optimize': 2}},
    windows = [
        {
            'script': 'wammu.py',
            'icon_resources': [(1, 'icon/wammu.ico')],
        },
        ],
    zipfile = "shared.lib"
    )
