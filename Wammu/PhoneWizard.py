# -*- coding: UTF-8 -*-
# vim: expandtab sw=4 ts=4 sts=4:
'''
Wammu - Phone manager
Phone configuration wizard
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

import wx
import wx.wizard
import Wammu.Paths
import Wammu.Wizard
import Wammu.Data
from Wammu.Utils import StrConv, Str_ as _


class PhoneDriverPage(Wammu.Wizard.ChoicePage):
    """
    Selects Gammu phone driver.
    """
    def __init__(self, parent, manufacturer):
        self.names = []
        connections = []
        helps = []

        self.names.append('at')
        connections.append(_('AT based'))
        if manufacturer in ['symbian', 'nokia']:
            helps.append(_('This provides minimal access to phone features. It is recommended to use other connection type.'))
        else:
            helps.append(_('Good choice for most phones except Nokia and Symbian based. Provides access to most phone features.'))

        if manufacturer in ['nokia', 'any']:
            self.names.append('fbus')
            connections.append(_('Nokia FBUS'))
            helps.append(_('Nokia proprietary protocol.'))

            self.names.append('mbus')
            connections.append(_('Nokia MBUS'))
            helps.append(_('Nokia proprietary protocol. Older version, use FBUS if possible.'))

        self.names.append('obex')
        connections.append(_('OBEX based'))
        helps.append(_('Standard access to filesystem and sometimes also to phone data. Good choice for recent phones.'))

        if manufacturer in ['symbian', 'any']:
            self.names.append('symbian')
            connections.append(_('Symbian using Gnapplet'))
            helps.append(_('You have to install Gnapplet into phone before using this connection. You can find it in Gammu sources.'))

        Wammu.Wizard.ChoicePage.__init__(self, parent,
                _('Connection type'),
                _('Please select connection type'),
                connections, helps)

    def SetManufacturer(self):
        return self.names[self.GetType()]


class PhoneManufacturerPage(Wammu.Wizard.ChoicePage):
    """
    Selects phone manufacturer.
    """
    def __init__(self, parent):
        self.names = []
        self.parent = parent
        connections = []
        helps = []

        self.names.append('any')
        connections.append(_('I don\'t know'))
        helps.append(_('Select this option only if really necessary. You will be provided with too much options in next step.'))

        self.names.append('nokia')
        connections.append(_('Nokia phone'))
        helps.append(_('If your phone runs Symbian, please select directly it.'))

        self.names.append('symbian')
        connections.append(_('Symbian based phone'))
        helps.append(_('Go on if your phone uses Symbian OS (regardless of manufacturer).'))

        self.names.append('nota')
        connections.append(_('None of the above'))
        helps.append(_('Select this option if nothing above matches, good choice for other manufacturers like Alcatel, BenQ, LG, Sharp, Sony Ericsson...'))

        Wammu.Wizard.ChoicePage.__init__(self, parent,
                _('Phone type'),
                _('Please select phone type'),
                connections, helps)

    def GetManufacturer(self):
        return self.names[self.GetType()]

    def GetNext(self):
        """
        Dynamically create next page for current settings.
        """
        next = PhoneDriverPage(self.parent, self.GetManufacturer())
        next.SetNext(Wammu.Wizard.ChoicePage.GetNext(self))
        next.SetPrev(self)
        return next



class PhoneConnectionPage(Wammu.Wizard.ChoicePage):
    """
    Selects phone connection type.
    """
    def __init__(self, parent, all = True):
        self.names = []
        connections = []
        helps = []

        if all:
            self.names.append('all')
            connections.append(_('Seach all connections'))
            helps.append(_('Wizard will search for all possible connections. It might take quite long time to search all possible connection types'))

        self.names.append('usb')
        connections.append(_('USB cable'))
        helps.append(_('Many phones now come with USB cable, select this if you\'re using this connection type.'))

        self.names.append('bluetooth')
        connections.append(_('Bluetooth'))
        helps.append(_('Bluetooth connection is wireless and does not require direct visibility. Phone needs to be properly paired with computer before proceeding.'))

        self.names.append('irda')
        connections.append(_('IrDA'))
        helps.append(_('IrDA wireless connection requires direct visibility, please make sure this is fullfilled and computer can see phone.'))

        self.names.append('serial')
        connections.append(_('Serial cable'))
        helps.append(_('This is not often used connection, but was very popular for older phones.'))

        Wammu.Wizard.ChoicePage.__init__(self, parent,
                _('Phone connection'),
                _('How is your phone connected?'),
                connections, helps)

    def GetConnectionType(self):
        return self.names[self.GetType()]


class ConfigTypePage(Wammu.Wizard.ChoicePage):
    def __init__(self, parent, pg0, pg1, pg2):
         Wammu.Wizard.ChoicePage.__init__(self, parent,
                _('Configuration type'),
                _('How do you want to configure your phone connection?'),
                [
                    _('Automatically search for a phone'),
                    _('Guided configuration'),
                    _('Manual configuration'),
                ],

                [
                    _('Wizard will attempt to search phone on usual ports.'),
                    _('You will be guided through configuration by phone connection type and vendor.'),
                    _('You know what you are doing and know exact parameters you need for connecting to phone.'),
                ],
                [ pg0, pg1, pg2])

def RunConfigureWizard(parent):
    """
    Executes wizard for configuring phone
    """
    bmp = wx.Bitmap(Wammu.Paths.MiscPath('phonewizard'))
    wiz = wx.wizard.Wizard(parent, -1, _('Wammu Phone Configuration Wizard'), bmp)

    # Create pages
    pg_title = Wammu.Wizard.SimplePage(wiz, _('Welcome'), 
            _('This wizard will help you with configuring phone connection in Wammu.'),
            [
                '',
                _('Please make sure you have phone ready:'),
                '- %s' % _('It is powered on.'),
                '- %s' % _('You have enabled connection method you want to use in it.'),
                '- %s' % _('Cable is connected or phone is in wireless connection range.'),
                '',
                _('As soon as your phone is ready, you can continue.'),
            ])

    pg_search1 = Wammu.Wizard.SimplePage(wiz, _('Phone conneciont'), _('1.'))
    pg_search1 = PhoneConnectionPage(wiz)

    pg_guide1 = PhoneConnectionPage(wiz, False)
    pg_guide2 = PhoneManufacturerPage(wiz)

    pg_manual1 = Wammu.Wizard.SimplePage(wiz, _('Manual configuration'), _('1.'))

    pg_type = ConfigTypePage(wiz, pg_search1, pg_guide1, pg_manual1)

    # Set their order
    pg_title.SetNext(pg_type)
    pg_type.SetPrev(pg_title)

    pg_type.SetNext(pg_search1) # overrided by it's GetNext
    pg_search1.SetPrev(pg_type)
    pg_guide1.SetPrev(pg_type)
    pg_manual1.SetPrev(pg_type)

    pg_guide1.SetNext(pg_guide2)
    pg_guide2.SetPrev(pg_guide1)

    # Resize wizard
    wiz.FitToPage(pg_title)

    # Execute wizar
    if wiz.RunWizard(pg_title):
        return "Configured"
    else:
        return None

class WizardApp(wx.App):
    def OnInit(self):

        self.SetAppName('Wammu Phone Configuration Wizard')
        vendor = StrConv(u'Michal Čihař')
        if vendor.find('?') != -1:
            vendor = 'Michal Čihař'
        self.SetVendorName(vendor)

        wx.InitAllImageHandlers()

        # Return a success flag
        return True
