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
import Wammu.SettingsStorage
from Wammu.Utils import StrConv, Str_ as _

class FinalPage(Wammu.Wizard.InputPage):
    """
    Shows result of configuration, and allow to name phone.
    """
    def __init__(self, parent):
        Wammu.Wizard.InputPage.__init__(self, parent,
                _('Configuration done'),
                _('Thank you for configuring phone connection.'),
                parent.settings.GetName(),
                _('You can enter any name which you will use to identify your phone.')
                )

    def GetNext(self):
        self.parent.settings.SetName(self.edit.GetValue())
        return Wammu.Wizard.InputPage.GetNext(self)

class PhonePortPage(Wammu.Wizard.InputPage):
    """
    Selects phone port.
    """
    def __init__(self, parent):
        ports, help = parent.settings.GetDevices()
        Wammu.Wizard.InputPage.__init__(self, parent,
                _('Phone port'),
                _('Please enter port where phone is connected:'),
                ports,
                help)

    def GetNext(self):
        self.parent.settings.SetPort(self.edit.GetValue())
        self.parent.pg_final.SetPrev(self)
        return self.parent.pg_final

class PhoneGammuDriverPage(Wammu.Wizard.ChoicePage):
    """
    Selects real Gammu phone driver.
    """
    def __init__(self, parent):
        self.names, connections, helps = parent.settings.GetGammuDrivers()

        if len(self.names) == 0:
            Wammu.Wizard.SimplePage.__init__(self, parent,
                    _('Driver to use'),
                    _('Sorry no driver matches your configuration, please return back and try different settings or manual configuration.'))
        else:
            Wammu.Wizard.ChoicePage.__init__(self, parent,
                    _('Driver to use'),
                    _('Please select which driver you want to use'),
                    connections, helps)

    def GetNext(self):
        """
        Dynamically create next page for current settings.
        """
        if len(self.names) == 0:
            return None
        self.parent.settings.SetGammuDriver(self.names[self.GetType()])
        next = PhonePortPage(self.parent)
        next.SetPrev(self)
        return next

class PhoneDriverPage(Wammu.Wizard.ChoicePage):
    """
    Selects Gammu phone driver type.
    """
    def __init__(self, parent):
        self.names, connections, helps = parent.settings.GetDrivers()

        Wammu.Wizard.ChoicePage.__init__(self, parent,
                _('Connection type'),
                _('Please select connection type'),
                connections, helps)

    def GetNext(self):
        """
        Dynamically create next page for current settings.
        """
        self.parent.settings.SetDriver(self.names[self.GetType()])
        next = PhoneGammuDriverPage(self.parent)
        next.SetPrev(self)
        return next

class PhoneManufacturerPage(Wammu.Wizard.ChoicePage):
    """
    Selects phone manufacturer.
    """
    def __init__(self, parent):
        self.names, connections, helps = parent.settings.GetManufacturers()

        Wammu.Wizard.ChoicePage.__init__(self, parent,
                _('Phone type'),
                _('Please select phone type'),
                connections, helps)

    def GetNext(self):
        """
        Dynamically create next page for current settings.
        """
        self.parent.settings.SetManufacturer(self.names[self.GetType()])
        next = PhoneDriverPage(self.parent)
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

    def GetNext(self):
        self.parent.settings.SetConnection(self.names[self.GetType()])
        return Wammu.Wizard.ChoicePage.GetNext(self)

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



def RunConfigureWizard(parent, position = 0):
    """
    Executes wizard for configuring phone
    """
    bmp = wx.Bitmap(Wammu.Paths.MiscPath('phonewizard'))
    wiz = wx.wizard.Wizard(parent, -1, _('Wammu Phone Configuration Wizard'), bmp)
    wiz.settings = Wammu.SettingsStorage.Settings()
    wiz.settings.SetPosition(position)

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

    pg_search1 = PhoneConnectionPage(wiz)

    pg_guide1 = PhoneConnectionPage(wiz, False)
    pg_guide2 = PhoneManufacturerPage(wiz)

    pg_manual1 = Wammu.Wizard.SimplePage(wiz, _('Manual configuration'), _('1.'))

    pg_type = ConfigTypePage(wiz, pg_search1, pg_guide1, pg_manual1)

    wiz.pg_final = FinalPage(wiz)

    # Set their order
    pg_title.SetNext(pg_type)
    pg_type.SetPrev(pg_title)

    pg_type.SetNext(pg_search1) # overrided by it's GetNext
    pg_search1.SetPrev(pg_type)
    pg_guide1.SetPrev(pg_type)
    pg_manual1.SetPrev(pg_type)

    pg_guide1.SetNext(pg_guide2)
    pg_guide2.SetPrev(pg_guide1)
    # rest of guide is created dynamically

    # Resize wizard
    wiz.FitToPage(pg_title)

    # Execute wizar
    if wiz.RunWizard(pg_title):
        return wiz.settings.GetSettings()
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
