# -*- coding: UTF-8 -*-
# Wammu - Phone manager
# Copyright (c) 2003 - 2004 Michal Čihař 
#
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the Free
# Software Foundation; either version 2 of the License.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for
# more details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc., 59 Temple
# Place, Suite 330, Boston, MA 02111-1307 USA
'''
Unexpected exception handler
'''

import Wammu
import wx
import gammu
import traceback
import sys
import locale

def Handler(type, value, tback):
    """User friendly error handling """
    print '--------------- System information ----------------'
    print 'Python       %s' % sys.version.split()[0]
    print 'wxPython     %s' % wx.VERSION_STRING
    print 'Wammu        %s' % Wammu.__version__
    ver = gammu.Version()
    print 'python-gammu %s' % ver[1]
    print 'Gammu        %s' % ver[0]
    loc = locale.getdefaultlocale()
    print 'locales      %s (%s)' % (loc[0], loc[1])
    print '-------------------- Traceback --------------------'
    traceback.print_exception(type, value, tback)
    print '---------------------------------------------------'
    if type == UnicodeEncodeError:
        print 'Unicode encoding error appeared, see question 1 in FAQ, how to solve this.'
        print
    print 'You have probably found a bug. You might help improving this software by'
    print 'sending above text and description how it was caused to michal@cihar.com.'
