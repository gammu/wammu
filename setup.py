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
Setup script for installation using distutils
'''

import distutils
import distutils.command.build
import distutils.command.build_scripts
import distutils.command.clean
import distutils.command.install
import distutils.command.install_data
from xml.etree import cElementTree as ElementTree
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
    HAVE_PY2EXE = True
except:
    HAVE_PY2EXE = False

# some defines
PYTHONGAMMU_REQUIRED = (0, 24)
WXPYTHON_REQUIRED = (2, 6, 2, 0)

# check if Python is called on the first line with this expression
first_line_re = re.compile('^#!.*python[0-9.]*([ \t].*)?$')


class build_scripts_wammu(distutils.command.build_scripts.build_scripts, object):
    '''
    This is mostly distutils copy, it just renames script according
    to platform (.pyw for Windows, without extension for others)
    '''
    def copy_scripts(self):
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
                distutils.log.info(
                    "copying and adjusting %s -> %s", script, self.build_dir
                )
                if not self.dry_run:
                    outf = open(outfile, "w")
                    if not distutils.sysconfig.python_build:
                        outf.write("#!%s%s\n" %
                                   (os.path.normpath(sys.executable),
                                    post_interp))
                    else:
                        outf.write("#!%s%s\n" % (
                            os.path.join(
                                distutils.sysconfig.get_config_var("BINDIR"),
                                "python" + distutils.sysconfig.get_config_var("EXE")
                            ),
                            post_interp
                        ))
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
                        distutils.log.info(
                            "changing mode of %s from %o to %o",
                            file, oldmode, newmode
                        )
                        os.chmod(file, newmode)


def list_message_files(package='wammu', suffix='.po'):
    """
    Return list of all found message files and their installation paths.
    """
    _files = glob.glob('locale/*/' + package + suffix)
    _list = []
    for _file in _files:
        # basename (without extension) is a locale name
        _locale = os.path.basename(os.path.dirname(_file))
        _list.append((_locale, _file, os.path.join(
            'share', 'locale', _locale, 'LC_MESSAGES', '%s.mo' % package)))
    return _list


class build_wammu(distutils.command.build.build, object):
    """
    Custom build command with locales support.
    """

    def build_desktop_file(self, translations):
        """
        Builds translated desktop files.
        """
        desktop = os.path.join(self.build_base, 'wammu.desktop')
        distutils.log.info('generating %s -> %s', 'wammu.desktop.in', desktop)
        in_desktop = file('wammu.desktop.in', 'r')
        out_desktop = file(desktop, 'w')
        for line in in_desktop:
            if line.startswith('_Name'):
                out_desktop.write('Name=%s\n' % msgfmt.DESKTOP_NAME)
                for loc in translations.keys():
                    if 'Name' in translations[loc]:
                        out_desktop.write('Name[%s]=%s\n' % (loc, translations[loc]['Name']))
            elif line.startswith('_GenericName'):
                out_desktop.write('GenericName=%s\n' % msgfmt.DESKTOP_GENERIC_NAME)
                for loc in translations.keys():
                    if 'GenericName' in translations[loc]:
                        out_desktop.write('GenericName[%s]=%s\n' % (loc, translations[loc]['GenericName']))
            elif line.startswith('_Comment'):
                out_desktop.write('Comment=%s\n' % msgfmt.DESKTOP_COMMENT)
                for loc in translations.keys():
                    if 'Comment' in translations[loc]:
                        out_desktop.write('Comment[%s]=%s\n' % (loc, translations[loc]['Comment']))
            elif line.startswith('_Keywords'):
                out_desktop.write('Keywords=%s\n' % msgfmt.DESKTOP_KEYWORDS)
                for loc in translations.keys():
                    if 'Keywords' in translations[loc]:
                        out_desktop.write('Keywords[%s]=%s\n' % (loc, translations[loc]['Keywords']))
            else:
                out_desktop.write(line)

    def build_appdata_file(self, translations):
        """
        Builds translated appdata files.
        """
        appdata = os.path.join(self.build_base, 'wammu.appdata.xml')
        distutils.log.info('generating %s -> %s', 'wammu.appdata.xml.in', appdata)
        in_appdata = file('wammu.appdata.xml.in', 'r')
        tree = ElementTree.parse(in_appdata)
        description = tree.find('description')
        p1 = ElementTree.SubElement(description, 'p')
        p1.text = msgfmt.DESKTOP_DESCRIPTION_1
        p2 = ElementTree.SubElement(description, 'p')
        p2.text = msgfmt.DESKTOP_DESCRIPTION_2
        for loc in translations.keys():
            translation = translations[loc]
            if 'Description_1' in translation and 'Description_2' in translation:
                p1 = ElementTree.SubElement(description, 'p')
                p1.set('xml:lang', loc)
                p1.text = translation['Description_1'].decode('utf-8')
                p2 = ElementTree.SubElement(description, 'p')
                p2.set('xml:lang', loc)
                p2.text = translation['Description_2'].decode('utf-8')
        tree.write(appdata, 'utf-8', True)

    def build_message_files(self):
        """
        For each locale/*.po, build .mo file in target locale directory.

        As a side effect we build wammu.desktop file with updated
        translations here.
        """
        translations = {}
        for (_locale, _src, _dst) in list_message_files():
            _build_dst = os.path.join(self.build_base, _dst)
            destdir = os.path.dirname(_build_dst)
            if not os.path.exists(destdir):
                self.mkpath(destdir)
            distutils.log.info('compiling %s -> %s' % (_src, _build_dst))
            msgfmt.make(_src, _build_dst)
            translations[_locale] = msgfmt.DESKTOP_TRANSLATIONS

        self.build_desktop_file(translations)
        self.build_appdata_file(translations)

    def check_requirements(self):
        print 'Checking for python-gammu ...',
        try:
            import gammu
            version = gammu.Version()
            print 'found version %s using Gammu %s ...' % (version[1], version[0]),

            pygver = tuple(map(int, version[1].split('.')))
            if pygver < PYTHONGAMMU_REQUIRED:
                print 'too old!'
                print 'You need python-gammu at least %s!' % '.'.join(map(str, PYTHONGAMMU_REQUIRED))
                print 'You can get it from <http://wammu.eu/python-gammu/>'
            else:
                print 'OK'
        except ImportError, message:
            print
            print 'Could not import python-gammu!'
            print 'You can get it from <http://wammu.eu/python-gammu/>'
            print 'Import failed with following error: %s' % message

        print 'Checking for wxPython ...',
        try:
            import wx
            print 'found version %s ...' % wx.VERSION_STRING,
            if wx.VERSION < WXPYTHON_REQUIRED:
                print 'too old!'
                print 'You need at least wxPython %s!' % '.'.join(map(str, WXPYTHON_REQUIRED))
                print 'You can get it from <http://www.wxpython.org>'
            elif not wx.USE_UNICODE:
                print 'not unicode!'
                print 'You need at least wxPython %s with unicode enabled!' % '.'.join(map(str, WXPYTHON_REQUIRED))
                print 'You can get it from <http://www.wxpython.org>'
            else:
                print 'OK'
        except ImportError:
            print
            print 'You need wxPython!'
            print 'You can get it from <http://www.wxpython.org>'

        print 'Checking for Bluetooth stack ...',
        try:
            import bluetooth
            print 'OK'
        except ImportError:
            print
            print 'WARNING: PyBluez not found, without it you can not search for bluetooth devices'
            print 'PyBluez can be downloaded from <http://org.csail.mit.edu/pybluez/>'

        if sys.platform == 'win32':
            print 'Checking for PyWin32 ...',
            try:
                import win32file
                import win32com
                import win32api
                print 'found'
            except ImportError:
                print 'not found!'
                print 'This module is now needed for Windows!'
                print 'PyWin32 can be downloaded from <https://sourceforge.net/projects/pywin32/>'
                sys.exit(1)

    def run(self):
        self.build_message_files()
        self.check_requirements()
        super(build_wammu, self).run()


class clean_wammu(distutils.command.clean.clean, object):
    """
    Custom clean command.
    """

    def run(self):
        if self.all:
            # remove share directory
            directory = os.path.join(self.build_base, 'share')
            if os.path.exists(directory):
                distutils.dir_util.remove_tree(directory, dry_run=self.dry_run)
            else:
                distutils.log.warn('\'%s\' does not exist -- can\'t clean it',
                                   directory)
        super(clean_wammu, self).run()


class install_data_wammu(distutils.command.install_data.install_data, object):
    """
    Install locales in addition to regullar data.
    """

    def run(self):
        """
        Install also .mo files.
        """
        # add .mo files to data files
        for (_locale, _src, _dst) in list_message_files():
            _build_dst = os.path.join('build', _dst)
            item = [os.path.dirname(_dst), [_build_dst]]
            self.data_files.append(item)

        # desktop file
        if sys.platform != 'win32':
            self.data_files.append((os.path.join('share', 'applications'), [os.path.join('build', 'wammu.desktop')]))
            self.data_files.append((os.path.join('share', 'appdata'), [os.path.join('build', 'wammu.appdata.xml')]))

        # install data files
        super(install_data_wammu, self).run()


py2exepackages = ['Wammu']
if sys.version_info >= (2, 5):
    # Email module changed a lot in python 2.5 and we can not yet use new API
    py2exepackages.append('email')
    py2exepackages.append('email.mime')

# ModuleFinder can't handle runtime changes to __path__, but win32com uses them
try:
    # if this doesn't work, try import modulefinder
    import py2exe.mf as modulefinder
    import win32com
    for p in win32com.__path__[1:]:
        modulefinder.AddPackagePath("win32com", p)
    for extra in ["win32com.shell"]:
        __import__(extra)
        m = sys.modules[extra]
        for p in m.__path__[1:]:
            modulefinder.AddPackagePath(extra, p)
except ImportError:
    # no build path setup, no worries.
    pass

addparams = {}

if HAVE_PY2EXE:
    addparams['windows'] = [
        {
            'script': 'wammu.py',
            'icon_resources': [(1, 'icon/wammu.ico')],
        },
        ]
    addparams['zipfile'] = 'shared.lib'

data_files = [
    (os.path.join('share', 'Wammu', 'images', 'icons'), glob.glob('images/icons/*.png')),
    (os.path.join('share', 'Wammu', 'images', 'misc'), glob.glob('images/misc/*.png')),
    ]

data_files.append((os.path.join('share', 'pixmaps'), [
    'icon/wammu.png',
    'icon/wammu.xpm',
    'icon/wammu.ico',
    'icon/wammu.svg',
    ]))
data_files.append((os.path.join('share', 'man', 'man1'), ['wammu.1', 'wammu-configure.1']))
data_files.append((os.path.join('share', 'man', 'cs', 'man1'), ['man/cs/wammu.1', 'man/cs/wammu-configure.1']))
data_files.append((os.path.join('share', 'man', 'de', 'man1'), ['man/de/wammu.1', 'man/de/wammu-configure.1']))
data_files.append((os.path.join('share', 'man', 'en_GB', 'man1'), ['man/en_GB/wammu.1', 'man/en_GB/wammu-configure.1']))
data_files.append((os.path.join('share', 'man', 'es', 'man1'), ['man/es/wammu.1', 'man/es/wammu-configure.1']))
data_files.append((os.path.join('share', 'man', 'et', 'man1'), ['man/et/wammu.1', 'man/et/wammu-configure.1']))
data_files.append((os.path.join('share', 'man', 'da', 'man1'), ['man/da/wammu.1', 'man/da/wammu-configure.1']))
data_files.append((os.path.join('share', 'man', 'fr', 'man1'), ['man/fr/wammu.1', 'man/fr/wammu-configure.1']))
data_files.append((os.path.join('share', 'man', 'hu', 'man1'), ['man/hu/wammu.1']))
data_files.append((os.path.join('share', 'man', 'id', 'man1'), ['man/id/wammu.1', 'man/id/wammu-configure.1']))
data_files.append((os.path.join('share', 'man', 'it', 'man1'), ['man/it/wammu.1', 'man/it/wammu-configure.1']))
data_files.append((os.path.join('share', 'man', 'nl', 'man1'), ['man/nl/wammu.1', 'man/nl/wammu-configure.1']))
data_files.append((os.path.join('share', 'man', 'pt_BR', 'man1'), ['man/pt_BR/wammu.1', 'man/pt_BR/wammu-configure.1']))
data_files.append((os.path.join('share', 'man', 'ru', 'man1'), ['man/ru/wammu.1', 'man/ru/wammu-configure.1']))
data_files.append((os.path.join('share', 'man', 'sk', 'man1'), ['man/sk/wammu.1', 'man/sk/wammu-configure.1']))
data_files.append((os.path.join('share', 'man', 'tr', 'man1'), ['man/sk/wammu.1', 'man/tr/wammu-configure.1']))
data_files.append((os.path.join('share', 'man', 'uk', 'man1'), ['man/sk/wammu.1', 'man/uk/wammu-configure.1']))

distutils.core.setup(
    name="wammu",
    version=Wammu.__version__,
    description="Wammu Mobile Phone Manager",
    long_description="Phone manager built on top of python-gammu. Supports many phones.",
    author=u"Michal Cihar",
    author_email="michal@cihar.com",
    maintainer=u"Michal Cihar",
    maintainer_email="michal@cihar.com",
    platforms=['Linux', 'Mac OSX', 'Windows XP/2000/NT', 'Windows 95/98/ME'],
    keywords=['mobile', 'phone', 'SMS', 'contact', 'gammu', 'calendar', 'todo'],
    url="http://wammu.eu/wammu/",
    download_url='http://wammu.eu/download/wammu/',
    license="GPL",
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Win32 (MS Windows)',
        'Environment :: X11 Applications :: GTK',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Operating System :: Microsoft :: Windows :: Windows 95/98/2000',
        'Operating System :: Microsoft :: Windows :: Windows NT/2000',
        'Operating System :: POSIX',
        'Operating System :: Unix',
        'Programming Language :: Python',
        'Topic :: Communications :: Telephony',
        'Topic :: Office/Business :: Scheduling',
        'Topic :: Utilities',
        'Natural Language :: English',
        'Natural Language :: Afrikaans',
        'Natural Language :: Catalan',
        'Natural Language :: Czech',
        'Natural Language :: German',
        'Natural Language :: Greek',
        'Natural Language :: Spanish',
        'Natural Language :: Estonian',
        'Natural Language :: Finnish',
        'Natural Language :: French',
        'Natural Language :: Galician',
        'Natural Language :: Hebrew',
        'Natural Language :: Hungarian',
        'Natural Language :: Indonesian',
        'Natural Language :: Italian',
        'Natural Language :: Korean',
        'Natural Language :: Dutch',
        'Natural Language :: Polish',
        'Natural Language :: Portuguese (Brazilian)',
        'Natural Language :: Russian',
        'Natural Language :: Slovak',
        'Natural Language :: Swedish',
        'Natural Language :: Chinese (Simplified)',
        'Natural Language :: Chinese (Traditional)',
    ],
    packages=['Wammu'],
    scripts=['wammu.py', 'wammu-configure.py'],
    data_files=data_files,
    # Override certain command classes with our own ones
    cmdclass={
        'build': build_wammu,
        'build_scripts': build_scripts_wammu,
        'clean': clean_wammu,
        'install_data': install_data_wammu,
        },
    # py2exe options
    options={'py2exe': {
            'optimize': 2,
            'packages': py2exepackages,
        }},
    **addparams
    )
