#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# vim: expandtab sw=4 ts=4 sts=4:
'''
Wammu - Phone manager
Setup script for installation using distutils
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

import distutils
import distutils.command.build
import distutils.command.build_scripts
import distutils.command.clean
import distutils.command.install
import distutils.command.install_data
from stat import ST_MODE
from wammu_setup import msgfmt
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

# used for passing state for skiping dependency check
skip_dependencies = False

# some defines
PYTHONGAMMU_REQUIRED = (0, 19)
WXPYTHON_REQUIRED = (2, 6, 2, 0)

# check if Python is called on the first line with this expression
first_line_re = re.compile('^#!.*python[0-9.]*([ \t].*)?$')

class build_scripts_wammu(distutils.command.build_scripts.build_scripts, object):
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
            script = distutils.util.convert_path(script)
            outfile = os.path.join(self.build_dir, os.path.splitext(os.path.basename(script))[0])
            if sys.platform == 'win32':
                outfile += os.extsep + 'pyw'
            outfiles.append(outfile)

            if not self.force and not distutils.dep_util.newer(script, outfile):
                distutils.log.debug("not copying %s (up-to-date)", script)
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
                distutils.log.info("copying and adjusting %s -> %s", script,
                         self.build_dir)
                if not self.dry_run:
                    outf = open(outfile, "w")
                    if not distutils.sysconfig.python_build:
                        outf.write("#!%s%s\n" %
                                   (os.path.normpath(sys.executable),
                                    post_interp))
                    else:
                        outf.write("#!%s%s\n" %
                                   (os.path.join(
                            distutils.sysconfig.get_config_var("BINDIR"),
                            "python" + distutils.sysconfig.get_config_var("EXE")),
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
                    distutils.log.info("changing mode of %s", file)
                else:
                    oldmode = os.stat(file)[ST_MODE] & 07777
                    newmode = (oldmode | 0555) & 07777
                    if newmode != oldmode:
                        distutils.log.info("changing mode of %s from %o to %o",
                                 file, oldmode, newmode)
                        os.chmod(file, newmode)

    # copy_scripts ()

def list_message_files(package = 'wammu', suffix = '.po'):
    """
    Return list of all found message files and their installation paths.
    """
    _files = glob.glob('locale/*' + suffix)
    _list = []
    for _file in _files:
        # basename (without extension) is a locale name
        _locale = os.path.splitext(os.path.basename(_file))[0]
        _list.append((_file, os.path.join(
            'share', 'locale', _locale, 'LC_MESSAGES', '%s.mo' % package)))
    return _list

class build_wammu(distutils.command.build.build, object):
    """
    Custom build command with locales support.
    """
    user_options = distutils.command.build.build.user_options + [('skip-deps', 's', 'skip checking for dependencies')]
    boolean_options = distutils.command.build.build.boolean_options + ['skip-deps']

    def initialize_options(self):
        global skip_dependencies
        super(build_wammu, self).initialize_options()
        self.skip_deps = skip_dependencies

    def finalize_options(self):
        global skip_dependencies
        super(build_wammu, self).finalize_options()
        if self.skip_deps:
            skip_dependencies = self.skip_deps

    def build_message_files (self):
        """
        For each locale/*.po, build .mo file in target locale directory.
        """
        for (_src, _dst) in list_message_files(self.distribution.get_name()):
            _build_dst = os.path.join('build', _dst)
            destdir = os.path.dirname(_build_dst)
            if not os.path.exists(destdir):
                self.mkpath(destdir)
            if not os.path.exists(_build_dst) or \
              (os.path.getmtime(_build_dst) < os.path.getmtime(_src)):
                distutils.log.info('compiling %s -> %s' % (_src, _build_dst))
                msgfmt.make(_src, _build_dst)

    def check_requirements(self):
        if os.getenv('SKIPGAMMUCHECK') == 'yes':
            print 'Skipping Gammu check, expecting you know what you are doing!'
        else:
            print 'Checking for python-gammu ...',
            try:
                import gammu
                version = gammu.Version()
                print 'found version %s using Gammu %s ...' % (version[1], version[0]),

                pygver = tuple(map(int, version[1].split('.')))
                if  pygver < PYTHONGAMMU_REQUIRED:
                    print 'too old!'
                    print 'You need python-gammu at least %s!' % '.'.join(map(str, PYTHONGAMMU_REQUIRED))
                    print 'You can get it from <http://cihar.com/gammu/python/>'
                    sys.exit(1)
                print 'OK'
            except ImportError, message:
                print 'Could not import python-gammu!'
                print 'You can get it from <http://cihar.com/gammu/python/>'
                print 'Import failed with following error: %s' % message
                sys.exit(1)

        if os.getenv('SKIPWXCHECK') == 'yes':
            print 'Skipping wxPython check, expecting you know what you are doing!'
        else:
            print 'Checking for wxPython ...',
            try:
                import wx
                print 'found version %s ...' % wx.VERSION_STRING,
                if wx.VERSION < WXPYTHON_REQUIRED:
                    print 'too old!'
                    print 'You need at least wxPython %s!' % '.'.join(map(str, WXPYTHON_REQUIRED))
                    print 'You can get it from <http://www.wxpython.org>'
                    sys.exit(1)
                if not wx.USE_UNICODE:
                    print 'not unicode!'
                    print 'You need at least wxPython %s with unicode enabled!' % '.'.join(map(str, WXPYTHON_REQUIRED))
                    print 'You can get it from <http://www.wxpython.org>'
                    sys.exit(1)
                print 'OK'
            except ImportError:
                print 'You need wxPython!'
                print 'You can get it from <http://www.wxpython.org>'
                sys.exit(1)

        print 'Checking for Bluetooth stack ...',
        try:
            import bluetooth
            print 'PyBluez found'
        except ImportError:
            try:
                import gnomebt.controller
                print 'GNOME Bluetooth found'
                print 'WARNING: GNOME Bluetooth support is limited, consider installing PyBluez'
            except ImportError:
                print 'WARNING: neither GNOME Bluetooth nor PyBluez found, without those you can not search for bluetooth devices'
            print 'PyBluez can be downloaded from <http://org.csail.mit.edu/pybluez/>'

        if sys.platform == 'win32':
            print 'Checking for PyWin32 ...',
            try:
                import win32file
                print 'win32file found'
            except ImportError:
                print 'win32file not found!'
                print 'PyWin32 can be downloaded from <https://sourceforge.net/projects/pywin32/>'
    def run (self):
        global skip_dependencies
        self.build_message_files()
        if not skip_dependencies:
            self.check_requirements()
        super(build_wammu, self).run()

class clean_wammu(distutils.command.clean.clean, object):
    """
    Custom clean command.
    """

    def run (self):
        if self.all:
            # remove share directory
            directory = os.path.join('build', 'share')
            if os.path.exists(directory):
                distutils.dir_util.remove_tree(directory, dry_run=self.dry_run)
            else:
                distutils.log.warn('\'%s\' does not exist -- can\'t clean it',
                                   directory)
        super(clean_wammu, self).run()

class install_wammu(distutils.command.install.install, object):
    """
    Install wrapper to support option for skipping deps
    """

    user_options = distutils.command.install.install.user_options + [('skip-deps', 's', 'skip checking for dependencies')]
    boolean_options = distutils.command.install.install.boolean_options + ['skip-deps']

    def initialize_options(self):
        global skip_dependencies
        super(install_wammu, self).initialize_options()
        self.skip_deps = skip_dependencies

    def finalize_options(self):
        global skip_dependencies
        super(install_wammu, self).finalize_options()
        if self.skip_deps:
            skip_dependencies = self.skip_deps

class install_data_wammu(distutils.command.install_data.install_data, object):
    """
    Install locales in addition to regullar data.
    """

    def run (self):
        """
        Install also .mo files.
        """
        # add .mo files to data files
        for (_src, _dst) in list_message_files(self.distribution.get_name()):
            _build_dst = os.path.join('build', _dst)
            item = [os.path.dirname(_dst), [_build_dst]]
            self.data_files.append(item)
        # install data files
        super(install_data_wammu, self).run()

py2exepackages = ['Wammu']
if sys.version_info >= (2, 5):
    # Email module changed a lot in python 2.5 and we can not yet use new API
    py2exepackages.append('email')
    py2exepackages.append('email.mime')

distutils.core.setup(name="wammu",
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
        'Translations :: Afrikaans',
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
        'Translations :: Russian',
        'Translations :: Slovak',
        'Translations :: Spanish',
        'Translations :: Swedish',
    ],
    packages = ['Wammu', 'Wammu.wxcomp'],
    scripts = ['wammu.py'],
    data_files = [
        (os.path.join('share','Wammu','images','icons'), glob.glob('images/icons/*.png')),
        (os.path.join('share','Wammu','images','misc'), glob.glob('images/misc/*.png')),
        (os.path.join('share','applications'), ['wammu.desktop']),
        (os.path.join('share','pixmaps'), ['icon/wammu.png', 'icon/wammu.xpm', 'icon/wammu.ico']),
        (os.path.join('share','man','man1'), ['wammu.1'])
        ],
    # Override certain command classes with our own ones
    cmdclass = {
        'build': build_wammu,
        'build_scripts': build_scripts_wammu,
        'clean': clean_wammu,
        'install': install_wammu,
        'install_data': install_data_wammu,
        },
    # py2exe options
    options = {'py2exe': {
            'optimize': 2,
            'packages': py2exepackages,
        }},
    windows = [
        {
            'script': 'wammu.py',
            'icon_resources': [(1, 'icon/wammu.ico')],
        },
        ],
    zipfile = "shared.lib"
    )
