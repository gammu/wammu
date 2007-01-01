# -*- coding: UTF-8 -*-
# vim: expandtab sw=4 ts=4 sts=4:
'''
Wammu - Phone manager
Phone configuration wizard
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

import wx
import wx.wizard
import Wammu.Paths
import Wammu.Wizard
import Wammu.Data
import Wammu.SettingsStorage
import Wammu.PhoneSearch
import Wammu.Events
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
        return Wammu.Wizard.InputPage.GetNext(self)

    def Blocked(self, evt):
        self.parent.settings.SetName(self.edit.GetValue())
        return False

    def Activated(self, evt):
        self.edit.SetValue(self.parent.settings.GetName())

class TestPage(Wammu.Wizard.SimplePage):
    """
    Tests phone connection.
    """
    def __init__(self, parent):
        Wammu.Wizard.SimplePage.__init__(self, parent, _('Connection test'))
        self.detail = wx.StaticText(self, -1, _('Wammu is now testing phone connection, please wait...'))
        self.detail.Wrap(400)
        self.sizer.Add(self.detail, 0, wx.ALL, 5)
        self.name = ''
        self.thread = None
        self.Bind(Wammu.Events.EVT_DATA, self.OnSearchEnd)

    def GetNext(self):
        self.parent.pg_final.SetPrev(self)
        return self.parent.pg_final

    def Activated(self, evt):
        if evt.GetDirection():
            self.detail.SetLabel(_('Wammu is now testing phone connection, please wait...'))
            device = self.parent.settings.GetPort()
            connection = self.parent.settings.GetGammuDriver()
            self.thread = Wammu.PhoneSearch.PhoneInfoThread(self, device, connection)
            self.thread.start()
            self.name = ''

    def OnSearchEnd(self, evt):
        self.thread = None
        if evt.data is None:
            self.detail.SetLabel(_('Phone not found!'))
            self.detail.Wrap(400)
        else:
            manuf = evt.data['Manufacturer']
            model = evt.data['Model'][0]
            self.name = '%s %s' % (manuf, model)
            self.parent.settings.SetName(self.name)
            self.detail.SetLabel(_('Phone has been found.\n\nManufacturer: %(manufacturer)s\nModel: %(model)s') % { 'manufacturer' : manuf, 'model' : model})
            self.detail.Wrap(400)

    def Blocked(self, evt):
        if self.thread is not None and self.thread.isAlive():
            wx.MessageDialog(self,
                _('Phone connection test is still active, you can not continue.'),
                _('Testing still active!'),
                wx.OK | wx.ICON_ERROR).ShowModal()
            return True
        if evt.GetDirection() and self.name == '':
            if wx.MessageDialog(self,
                _('Phone has not been found, are you sure you want to continue?'),
                _('Phone not found!'),
                wx.YES_NO | wx.NO_DEFAULT | wx.ICON_ERROR).ShowModal() == wx.ID_YES:
                return False
            return True
        return False

    def Cancel(self, evt):
        if self.thread is not None and self.thread.isAlive():
            wx.MessageDialog(self,
                _('Phone connection test is still active, you can not continue.'),
                _('Testing still active!'),
                wx.OK | wx.ICON_ERROR).ShowModal()
            return False
        return True

class PhoneSearchPage(Wammu.Wizard.TextPage):
    """
    Search for phone.
    """
    def __init__(self, parent):
        Wammu.Wizard.TextPage.__init__(self, parent,
                _('Phone search'),
                _('Phone searching status') + ':')

    def GetNext(self):
#        self.parent.settings.SetPort(self.edits[0].GetValue())
#        self.parent.settings.SetGammuDriver(self.edits[1].GetValue())
        self.parent.pg_test.SetPrev(self)
        return self.parent.pg_test

    def Blocked(self, evt):
        return False

class ManualPage(Wammu.Wizard.MultiInputPage):
    """
    Manual phone configuration.
    """
    def __init__(self, parent):
        """
        @todo: We should rather use SettingsStorage to get all valid devices.
        """
        Wammu.Wizard.MultiInputPage.__init__(self, parent,
                _('Manual configuration'),
                [
                    _('Port where phone is connected') + ':',
                    _('Connection type') + ':',
                ],
                [
                    Wammu.Data.Devices,
                    Wammu.Data.Connections,
                ])

    def GetNext(self):
        self.parent.settings.SetPort(self.edits[0].GetValue())
        self.parent.settings.SetGammuDriver(self.edits[1].GetValue())
        self.parent.pg_test.SetPrev(self)
        return self.parent.pg_test

    def Blocked(self, evt):
        if evt.GetDirection():
            if self.edits[0].GetValue() == '':
                wx.MessageDialog(self,
                    _('You need to select port which will be used.'),
                    _('No port selected!'),
                    wx.OK | wx.ICON_ERROR).ShowModal()
                return True
            if self.edits[1].GetValue() == '':
                wx.MessageDialog(self,
                    _('You need to select connection type which will be used.'),
                    _('No connection selected!'),
                    wx.OK | wx.ICON_ERROR).ShowModal()
                return True
        return False

class PhonePortPage(Wammu.Wizard.InputPage):
    """
    Selects phone port.
    """
    def __init__(self, parent):
        ports, help = parent.settings.GetDevices()
        Wammu.Wizard.InputPage.__init__(self, parent,
                _('Phone port'),
                _('Please enter port where phone is connected') + ':',
                ports,
                help)

    def GetNext(self):
        self.parent.settings.SetPort(self.edit.GetValue())
        self.parent.pg_test.SetPrev(self)
        return self.parent.pg_test

    def Blocked(self, evt):
        if evt.GetDirection() and self.edit.GetValue() == '':
            wx.MessageDialog(self,
                _('You need to select port which will be used.'),
                _('No port selected!'),
                wx.OK | wx.ICON_ERROR).ShowModal()
            return True
        return False

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
    def __init__(self, parent, search = True):
        self.names = []
        self.search = search
        connections = []
        helps = []

        if search:
            self.names.append('all')
            connections.append(_('Search all connections'))
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
    """
    Allows user to select how to configure phone.
    """
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


class ConfigureWizard:
    def __init__(self, parent, position = 0):
        bmp = wx.Bitmap(Wammu.Paths.MiscPath('phonewizard'))
        self.wiz = wx.wizard.Wizard(parent, -1, _('Wammu Phone Configuration Wizard'), bmp)
        self.wiz.settings = Wammu.SettingsStorage.Settings()
        self.wiz.settings.SetPosition(position)

        self.wiz.Bind(wx.wizard.EVT_WIZARD_PAGE_CHANGING, self.OnPageChanging)
        self.wiz.Bind(wx.wizard.EVT_WIZARD_PAGE_CHANGED, self.OnPageChanged)
        self.wiz.Bind(wx.wizard.EVT_WIZARD_CANCEL, self.OnCancel)

        # Create pages
        self.pg_title = Wammu.Wizard.SimplePage(self.wiz, _('Welcome'),
                _('This wizard will help you with configuring phone connection in Wammu.'),
                [
                    '',
                    _('Please make sure you have phone ready') + ':',
                    '- %s' % _('It is powered on.'),
                    '- %s' % _('Cable is connected or phone is in wireless connection range.'),
                    '- %s' % _('You have enabled Bluetooth or IrDA if you want to use in it.'),
                    '',
                    _('As soon as your phone is ready, you can continue.'),
                ])

        self.pg_search1 = PhoneConnectionPage(self.wiz)
        self.pg_search2 = PhoneSearchPage(self.wiz)

        self.pg_guide1 = PhoneConnectionPage(self.wiz, False)
        self.pg_guide2 = PhoneManufacturerPage(self.wiz)

        self.pg_manual1 = ManualPage(self.wiz)

        self.pg_type = ConfigTypePage(self.wiz, self.pg_search1, self.pg_guide1, self.pg_manual1)

        self.pg_final = FinalPage(self.wiz)
        self.pg_test = TestPage(self.wiz)
        self.wiz.pg_final = self.pg_final
        self.wiz.pg_test = self.pg_test

        # Set their order
        self.pg_title.SetNext(self.pg_type)
        self.pg_type.SetPrev(self.pg_title)

        self.pg_type.SetNext(self.pg_search1) # overrided by it's GetNext

        # Set previous page for all types
        self.pg_search1.SetPrev(self.pg_type)
        self.pg_guide1.SetPrev(self.pg_type)
        self.pg_manual1.SetPrev(self.pg_type)

        self.pg_guide1.SetNext(self.pg_guide2)
        self.pg_guide2.SetPrev(self.pg_guide1)
        # rest of guide is created dynamically

        self.pg_search1.SetNext(self.pg_search2)
        self.pg_search2.SetPrev(self.pg_search1)
        # rest of search is created dynamically

        # Resize wizard
        self.wiz.FitToPage(self.pg_title)

    def OnPageChanging(self, evt):
        if evt.GetPage().Blocked(evt):
            evt.Veto()

    def OnPageChanged(self, evt):
        evt.GetPage().Activated(evt)

    def OnCancel(self, evt):
        if not evt.GetPage().Cancel(evt):
            evt.Veto()

    def Run(self):
        return self.wiz.RunWizard(self.pg_title)

    def Do(self):
        if self.Run():
            return self.wiz.settings.GetSettings()
        else:
            return None


def RunConfigureWizard(parent, position = 0):
    """
    Executes wizard for configuring phone
    """
    return ConfigureWizard(parent, position).Do()

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
