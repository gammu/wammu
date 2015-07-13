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
Phone configuration wizard
'''

import wx
import wx.wizard
import Wammu.Paths
import Wammu.Wizard
import Wammu.Data
import Wammu.SettingsStorage
import Wammu.PhoneSearch
import Wammu.Events
import Wammu.Utils
import wx.lib.hyperlink
from Wammu.Locales import StrConv
from Wammu.Locales import ugettext as _


class FinalPage(Wammu.Wizard.InputPage):
    """
    Shows result of configuration, and allow to name phone.
    """
    def __init__(self, parent):
        Wammu.Wizard.InputPage.__init__(
            self, parent,
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
        self.detail = wx.StaticText(
                self,
                -1,
                _('Wammu is now testing phone connection, please wait...'))
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
            self.detail.SetLabel(
                    _('Wammu is now testing phone connection, please wait...'))
            device = self.parent.settings.GetPort()
            connection = self.parent.settings.GetGammuDriver()
            self.thread = Wammu.PhoneSearch.PhoneInfoThread(self, device, connection)
            self.thread.start()
            self.name = ''

    def OnSearchEnd(self, evt):
        self.thread = None
        if evt.data is None:
            self.detail.SetLabel('%s\n%s' % (
                    evt.error[0],
                    evt.error[1]
                    ))
            self.detail.Wrap(400)
        else:
            manuf = evt.data['Manufacturer']
            model = evt.data['Model'][0]
            self.name = '%s %s' % (manuf, model)
            self.parent.settings.SetName(self.name)
            self.detail.SetLabel(
                _('Phone has been found.') +
                (_('Manufacturer: %(manufacturer)s\nModel: %(model)s') % {
                    'manufacturer': manuf, 'model': model
                })
            )
            self.detail.Wrap(400)

    def Blocked(self, evt):
        if self.thread is not None and self.thread.isAlive():
            wx.MessageDialog(
                self,
                _('Phone connection test is still active, you can not continue.'),
                _('Testing still active!'),
                wx.OK | wx.ICON_ERROR
            ).ShowModal()
            return True
        if evt.GetDirection() and self.name == '':
            dialog = wx.MessageDialog(
                self,
                _('Phone has not been found, are you sure you want to continue?'),
                _('Phone not found!'),
                wx.YES_NO | wx.NO_DEFAULT | wx.ICON_ERROR)
            if dialog.ShowModal() == wx.ID_YES:
                return False
            return True
        return False

    def Cancel(self, evt):
        # FIXME: we should abort test here
        if self.thread is not None and self.thread.isAlive():
            wx.MessageDialog(
                self,
                _('Phone connection test is still active, you can not continue.'),
                _('Testing still active!'),
                wx.OK | wx.ICON_ERROR
            ).ShowModal()
            return False
        return True

class PhoneSearchPage(Wammu.Wizard.TextPage):
    """
    Search for phone.
    """
    def __init__(self, parent):
        Wammu.Wizard.TextPage.__init__(
            self, parent,
            _('Phone search'),
            _('Phone searching status') + ':'
        )
        self.Bind(Wammu.Events.EVT_DONE, self.OnDone)
        self.Bind(Wammu.Events.EVT_TEXT, self.OnText)
        self.Bind(Wammu.Events.EVT_SHOW_MESSAGE, self.OnShowMessage)
        self.results = []
        self.thread = None

    def GetNext(self):
        self.parent.pg_test.SetPrev(self)
        return self.parent.pg_test

    def Blocked(self, evt):
        if self.thread is not None and self.thread.isAlive():
            wx.MessageDialog(
                self,
                _('Phone search is still active, you can not continue.'),
                _('Searching still active!'),
                wx.OK | wx.ICON_ERROR
            ).ShowModal()
            return True
        if evt.GetDirection() and len(self.results) == 0:
            wx.MessageDialog(
                self,
                _('No phone has not been found, you can not continue.'),
                _('No phone found!'),
                wx.OK | wx.ICON_ERROR
            ).ShowModal()
            return True
        return False

    def Cancel(self, evt):
        # FIXME: we should abort searching here
        if self.thread is not None and self.thread.isAlive():
            wx.MessageDialog(
                self,
                _('Phone search is still active, you can not continue.'),
                _('Searching still active!'),
                wx.OK | wx.ICON_ERROR
            ).ShowModal()
            return False
        return True

    def Activated(self, evt):
        if evt.GetDirection():
            self.edit.Clear()
            self.edit.AppendText(_('Wammu is now searching for phone:') + '\n')
            self.thread = Wammu.PhoneSearch.AllSearchThread(
                lock=False,
                callback=self.SearchDone,
                msgcallback=self.SearchMessage,
                noticecallback=self.SearchNotice,
                limit=self.parent.settings.GetConnection(),
                win=self
            )
            self.thread.start()
            self.results = []

    def SearchNotice(self, title, text):
        evt = Wammu.Events.ShowMessageEvent(
            message=text,
            title=title,
            type=wx.ICON_WARNING
        )
        wx.PostEvent(self, evt)

    def SearchMessage(self, text):
        """
        This has to send message as it is called from different thread.
        """
        evt = Wammu.Events.TextEvent(text=text + '\n')
        wx.PostEvent(self, evt)

    def SearchDone(self, lst):
        """
        This has to send message as it is called from different thread.
        """
        self.results = lst
        evt = Wammu.Events.DoneEvent()
        wx.PostEvent(self, evt)

    def OnText(self, evt):
        self.edit.AppendText(StrConv(evt.text))

    def OnShowMessage(self, evt):
        wx.MessageDialog(
            self.parent,
            StrConv(evt.message),
            StrConv(evt.title),
            wx.OK | evt.type
        ).ShowModal()

    def OnDone(self, evt):
        """
        Select one config to use.
        """
        if len(self.results) == 0:
            self.edit.AppendText(_('No phone has been found!') + '\n')
            return
        if len(self.results) > 1:
            # Allow user to select phone
            # FIXME: Might be in wizard, but this should be rare...
            choices = []
            for phone in self.results:
                choices.append(
                    _('Phone %(manufacturer)s %(model)s on device %(port)s using connection %(connection)s') %
                    {
                        'model': phone[2][0],
                        'manufacturer': phone[3],
                        'port': phone[0],
                        'connection': phone[1]
                    })
            dlg = wx.SingleChoiceDialog(
                self,
                _('Select phone to use from below list'),
                _('Select phone'),
                choices
            )
            if dlg.ShowModal() == wx.ID_OK:
                idx = dlg.GetSelection()
                config = self.results[idx]
            else:
                self.results = []
                config = None
        else:
            # Use directly only found phone
            config = self.results[0]

        if config is not None:
            self.parent.settings.SetPort(config[0])
            self.parent.settings.SetGammuDriver(config[1])
            self.edit.AppendText(_('Following phone will be used:') + '\n')
            self.edit.AppendText(
                _('Phone %(manufacturer)s %(model)s on device %(port)s using connection %(connection)s') %
                {
                    'model': config[2][0],
                    'manufacturer': config[3],
                    'port': config[0],
                    'connection': config[1]
                })
        else:
            self.edit.AppendText(_('No phone selected!') + '\n')


class ManualPage(Wammu.Wizard.MultiInputPage):
    """
    Manual phone configuration.
    """
    def __init__(self, parent):
        Wammu.Wizard.MultiInputPage.__init__(
            self, parent,
            _('Manual configuration'),
            [
                _('Device where phone is connected') + ':',
                _('Connection type') + ':',
            ],
            [
                parent.settings.GetDevices()[0],
                Wammu.Data.Connections,
            ]
        )

    def GetNext(self):
        self.parent.settings.SetPort(self.edits[0].GetValue())
        self.parent.settings.SetGammuDriver(self.edits[1].GetValue())
        self.parent.pg_test.SetPrev(self)
        return self.parent.pg_test

    def Blocked(self, evt):
        if evt.GetDirection():
            if self.edits[0].GetValue() == '':
                wx.MessageDialog(
                    self,
                    _('You need to select device which will be used.'),
                    _('No device selected!'),
                    wx.OK | wx.ICON_ERROR
                ).ShowModal()
                return True
            if self.edits[1].GetValue() == '':
                wx.MessageDialog(
                    self,
                    _('You need to select connection type which will be used.'),
                    _('No connection selected!'),
                    wx.OK | wx.ICON_ERROR
                ).ShowModal()
                return True
        return False

class PhonePortPage(Wammu.Wizard.InputPage):
    """
    Selects phone device.
    """
    def __init__(self, parent):
        ports, helptext = parent.settings.GetDevices()
        Wammu.Wizard.InputPage.__init__(
            self, parent,
            _('Phone Device'),
            _('Please enter device where phone is accessible') + ':',
            ports,
            helptext
        )

    def GetNext(self):
        self.parent.settings.SetPort(self.edit.GetValue())
        self.parent.pg_test.SetPrev(self)
        return self.parent.pg_test

    def Blocked(self, evt):
        if evt.GetDirection() and self.edit.GetValue() == '':
            wx.MessageDialog(
                self,
                _('You need to select device which will be used.'),
                _('No device selected!'),
                wx.OK | wx.ICON_ERROR
            ).ShowModal()
            return True
        return False

class PhoneGammuDriverPage(Wammu.Wizard.ChoicePage):
    """
    Selects real Gammu phone driver.
    """
    def __init__(self, parent):
        self.names, connections, helps = parent.settings.GetGammuDrivers()

        if len(self.names) == 0:
            Wammu.Wizard.SimplePage.__init__(
                self, parent,
                _('Driver to use'),
                _('Sorry no driver matches your configuration, please return back and try different settings or manual configuration.')
            )
        else:
            Wammu.Wizard.ChoicePage.__init__(
                self, parent,
                _('Driver to use'),
                _('Driver to use'),
                connections, helps,
                extratext=_('Please select which driver you want to use. Follow the help text shown below to select the best one.')
            )

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

        Wammu.Wizard.ChoicePage.__init__(
            self,
            parent,
            _('Connection type'),
            _('Connection type'),
            connections, helps,
            extratext=_('Please select connection type, default choice should be best in most cases.')
        )

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

        Wammu.Wizard.ChoicePage.__init__(
            self, parent,
            _('Phone type'),
            _('Phone type'),
            connections, helps,
            extratext=_('Please select phone manufacturer or type. Try to be as specific as possible.'),
        )

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
    def __init__(self, parent, search=True):
        self.names = []
        self.search = search
        connections = []
        helps = []

        if search:
            self.names.append('all')
            connections.append(_('Search all connections'))
            helps.append(_('Wizard will search for all possible connections. It might take quite long time to search all possible connection types.'))

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

        Wammu.Wizard.ChoicePage.__init__(
            self, parent,
            _('Connection type'),
            _('Connection type'),
            connections, helps,
            extratext=_('How is your phone connected?'),
        )

    def GetNext(self):
        self.parent.settings.SetConnection(self.names[self.GetType()])
        return Wammu.Wizard.ChoicePage.GetNext(self)

class ConfigTypePage(Wammu.Wizard.ChoicePage):
    """
    Allows user to select how to configure phone.
    """
    def __init__(self, parent, pg0, pg1, pg2):
        Wammu.Wizard.ChoicePage.__init__(
            self, parent,
            _('Configuration style'),
            _('Configuration style'),
            [
                _('Guided configuration'),
                _('Automatically search for a phone'),
                _('Manual configuration'),
            ],

            [
                _('You will be guided through configuration by phone connection type and vendor.'),
                _('Wizard will attempt to search phone on usual ports.'),
                _('You know what you are doing and know exact parameters you need for connecting to phone.'),
            ],
            [pg0, pg1, pg2],
            extratext=_('How do you want to configure your phone connection?'),
        )
        self.info = wx.StaticText(
            self,
            -1,
            _('If you have no idea how to configure your phone connection, you can look at Gammu Phone Database for other users experiences:'))
        self.info.Wrap(400)
        self.sizer.Add(self.info, 0, wx.ALL, 5)
        self.link = wx.lib.hyperlink.HyperLinkCtrl(
                self,
                -1,
                'http://%scihar.com/gammu/phonedb' % Wammu.Utils.GetWebsiteLang())
        self.sizer.Add(self.link, 0, wx.ALL, 5)

class WelcomePage(Wammu.Wizard.SimplePage):
    """
    First page of Wizard.
    """
    def __init__(self, parent):
        Wammu.Wizard.SimplePage.__init__(
            self, parent,
            _('Welcome'),
            _('This wizard will help you with configuring phone connection in Wammu.'),
            [
                '',
                _('Please make sure you have phone ready, powered on and one of connection methods is set up:'),
                '  - %s' % _('Cable is connected.'),
                '  - %s' % _('You have enabled IrDA and phone is in visible range.'),
                '  - %s' % _('You have paired Bluetooth with computer.'),
                '',
                _('As soon as your phone is ready, you can continue.'),
            ]
        )

class ConfigureWizard:
    def __init__(self, parent, position=0):
        bmp = wx.Bitmap(Wammu.Paths.MiscPath('phonewizard'))
        self.wiz = wx.wizard.Wizard(
                parent,
                -1,
                _('Wammu Phone Configuration Wizard'),
                bmp)
        self.wiz.settings = Wammu.SettingsStorage.Settings()
        self.wiz.settings.SetPosition(position)

        self.wiz.Bind(wx.wizard.EVT_WIZARD_PAGE_CHANGING, self.OnPageChanging)
        self.wiz.Bind(wx.wizard.EVT_WIZARD_PAGE_CHANGED, self.OnPageChanged)
        self.wiz.Bind(wx.wizard.EVT_WIZARD_CANCEL, self.OnCancel)

        # Create pages
        self.pg_title = WelcomePage(self.wiz)

        self.pg_search1 = PhoneConnectionPage(self.wiz)
        self.pg_search2 = PhoneSearchPage(self.wiz)

        self.pg_guide1 = PhoneConnectionPage(self.wiz, False)
        self.pg_guide2 = PhoneManufacturerPage(self.wiz)

        self.pg_manual1 = ManualPage(self.wiz)

        self.pg_type = ConfigTypePage(
                self.wiz,
                self.pg_guide1,
                self.pg_search1,
                self.pg_manual1)

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

    def Execute(self):
        if self.Run():
            return self.wiz.settings.GetSettings()
        else:
            return None


def RunConfigureWizard(parent, position=0):
    """
    Executes wizard for configuring phone
    """
    return ConfigureWizard(parent, position).Execute()

class WizardApp(wx.App):
    def OnInit(self):

        self.SetAppName('Wammu Phone Configuration Wizard')
        vendor = StrConv(u'Michal Čihař')
        if vendor.find('?') != -1:
            vendor = 'Michal Čihař'
        self.SetVendorName(vendor)

        # Return a success flag
        return True
