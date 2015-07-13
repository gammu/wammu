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
SMS export code.
'''

import os
import imaplib
import wx
import Wammu.MailWriter
import Wammu.IMAP
import re
from Wammu.Locales import ugettext as _


MAILBOX_RE = re.compile(r'\((?P<flags>(\s*\\\w*)*)\)\s+(?P<delim>[^ ]*)\s+(?P<name>.*)')
POSSIBLY_QUOTED_RE = re.compile(r'"?([^"]*)"?')

def SMSToMailbox(parent, messages, contacts):
    count = len(messages)
    wildcard = _('Mailboxes') + ' (*.mbox)|*.mbox|' + _('All files') + ' (*.*)|*.*;*'
    exts = ['mbox']
    exts.append(None)
    dlg = wx.FileDialog(parent, _('Select mailbox file...'), os.getcwd(), "", wildcard, wx.SAVE | wx.OVERWRITE_PROMPT | wx.CHANGE_DIR)

    if dlg.ShowModal() != wx.ID_OK:
        return

    path = dlg.GetPath()
    ext = exts[dlg.GetFilterIndex()]
    # Add automatic extension if we know one and file does not
    # have any
    if (os.path.splitext(path)[1] == '' and
            ext is not None):
        path += '.' + ext

    parent.ShowProgress(_('Saving messages to mailbox'))
    try:
        f = file(path, 'w')
        for i in range(count):
            if not parent.progress.Update(i * 100 / count):
                del parent.progress
                parent.SetStatusText(_('Export terminated'))
                return

            sms = messages[i]
            filename, data, unused_msgid = Wammu.MailWriter.SMSToMail(parent.cfg, sms, contacts, True)
            f.write(data)
            f.write('\n')
            f.write('\n')

        f.close()
    except IOError:
        del parent.progress
        wx.MessageDialog(
            parent,
            _('Creating of file %s failed, bailing out.') % path,
            _('Can not create file!'),
            wx.OK | wx.ICON_ERROR
        ).ShowModal()
        del parent.progress
        parent.SetStatusText(_('Export terminated'))
        return

    parent.progress.Update(100)
    del parent.progress
    parent.SetStatusText(
        _('%(count)d messages exported to "%(path)s" (%(type)s)') % {
            'count': count,
            'path': path,
            'type': _('mailbox')
        }
    )

def SMSToMaildir(parent, messages, contacts):
    count = len(messages)
    dlg = wx.DirDialog(
        parent,
        _('Select maildir directory where to save files'),
        os.getcwd(),
        style=wx.DD_DEFAULT_STYLE | wx.DD_NEW_DIR_BUTTON
    )

    if dlg.ShowModal() != wx.ID_OK:
        return

    path = dlg.GetPath()
    outpath = path

    if not os.path.isdir(os.path.join(outpath, 'new')):
        res = wx.MessageDialog(
            parent,
            _('Selected folder does not contain new subfolder and thus probably is not valid maildir.\n\nDo you want to create new subfolder and export to it?'),
            _('Folder doesn\'t look like maildir!'),
            wx.YES_NO | wx.YES_DEFAULT | wx.CANCEL | wx.ICON_WARNING
        ).ShowModal()

        if res == wx.ID_CANCEL:
            return

        if res == wx.ID_YES:
            outpath = os.path.join(outpath, 'new')
            try:
                os.mkdir(outpath)
            except OSError:
                wx.MessageDialog(
                    parent,
                    _('Creating of folder failed, bailing out.'),
                    _('Can not create folder!'),
                    wx.OK | wx.ICON_ERROR
                ).ShowModal()
                return
    else:
        outpath = os.path.join(outpath, 'new')

    parent.ShowProgress(_('Saving messages to maildir'))
    for i in range(count):
        if not parent.progress.Update(i * 100 / count):
            del parent.progress
            parent.SetStatusText(_('Export terminated'))
            return

        sms = messages[i]
        filename, data, unused_msgid = Wammu.MailWriter.SMSToMail(parent.cfg, sms, contacts)

        outfile = os.path.join(outpath, filename)
        if os.path.exists(outfile):
            res = wx.MessageDialog(
                parent,
                _('Output file already exists, this usually means that this message was already saved there.\n\nDo you wish to overwrite file %s?') % outfile,
                _('File already exists!'),
                wx.YES_NO | wx.NO_DEFAULT | wx.CANCEL | wx.ICON_WARNING
            ).ShowModal()

            if res == wx.ID_CANCEL:
                del parent.progress
                parent.SetStatusText(_('Export terminated'))
                return

            if res == wx.ID_NO:
                continue
        try:
            f = file(outfile, 'w')
            f.write(data)
            f.close()
        except IOError:
            wx.MessageDialog(
                parent,
                _('Creating of file %s failed, bailing out.') % outfile,
                _('Can not create file!'),
                wx.OK | wx.ICON_ERROR
            ).ShowModal()
            del parent.progress
            parent.SetStatusText(_('Export terminated'))
            return

    parent.progress.Update(100)
    del parent.progress

    parent.SetStatusText(
        _('%(count)d messages exported to "%(path)s" (%(type)s)') % {
            'count': count,
            'path': path,
            'type': _('maildir')
        }
    )

def ParseIMAPFolder(item):
    '''
    Parses folder reply from IMAP.
    '''
    match = MAILBOX_RE.match(item)

    if not match:
        return (None, None)

    delim = POSSIBLY_QUOTED_RE.match(match.group('delim')).group(1)
    path = POSSIBLY_QUOTED_RE.match(match.group('name')).group(1)
    flags = match.group('flags')
    return (path, flags)

def SMSToIMAP(parent, messages, contacts):
    imapConfig = IMAPConfigHelper(parent.cfg)

    while True:
        value = IMAPSettingsDialog(parent, imapConfig).ShowModal()
        if value == wx.ID_CANCEL:
             return

        busy = wx.BusyInfo(_('Connecting to IMAP server...'))

        if imapConfig.useSSL:
            m = imaplib.IMAP4_SSL(imapConfig.server, int(imapConfig.port))
        else:
            m = imaplib.IMAP4(imapConfig.server, int(imapConfig.port))

        try:
            res = m.login(imapConfig.login, imapConfig.password)
        except:
            res = ['FAIL']
        del busy
        if res[0] == 'OK':
            break
        else:
            dialog = wx.MessageDialog(
                parent,
                _('Can not login, you probably entered invalid login information. Do you want to retry?'),
                _('Login failed!'),
                wx.YES_NO | wx.YES_DEFAULT | wx.ICON_ERROR
            )
            if dialog.ShowModal() == wx.ID_NO:
                return

    busy = wx.BusyInfo(_('Listing folders on IMAP server...'))
    try:
        res, list = m.list()
    except:
        res = 'FAIL'
    del busy
    if res != 'OK':
        wx.MessageDialog(
            parent,
            _('Can not list folders on server, bailing out.'),
            _('Listing failed!'),
            wx.OK | wx.ICON_ERROR
        ).ShowModal()
        parent.SetStatusText(_('Export terminated'))
        return

    folders = []
    for item in list:
        path, flags = ParseIMAPFolder(item)

        if path is None:
            continue

        if flags.find('\\Noselect') != -1:
            continue

        try:
            folders.append(unicode(path, 'imap4-utf-7'))
        except UnicodeDecodeError:
            # Ignore folders which can not be properly converted
            pass

    folders.sort()

    lastFolder = parent.cfg.Read('/IMAP/LastUsedFolder')
    folderIndex = 0
    if lastFolder != '':
        try:
            folderIndex = folders.index(lastFolder)
        except:
            pass

    dlg = wx.SingleChoiceDialog(
        parent,
        _('Please select folder on server %s where messages will be stored') % imapConfig.server,
        _('Select folder'),
        folders, wx.CHOICEDLG_STYLE | wx.RESIZE_BORDER
    )
    if folderIndex > 0:
        dlg.SetSelection(folderIndex)
    if dlg.ShowModal() == wx.ID_CANCEL:
        try:
            m.logout()
        except:
            pass
        return
    path = '%s@%s/%s' % (imapConfig.login, imapConfig.server, folders[dlg.GetSelection()])
    folder = folders[dlg.GetSelection()].encode('imap4-utf-7')

    parent.cfg.Write('/IMAP/LastUsedFolder', folders[dlg.GetSelection()])

    busy = wx.BusyInfo(_('Selecting folder on IMAP server...'))
    try:
        res = m.select(folder)
    except:
        res = ['FAIL']
    del busy
    if res[0] != 'OK':
        wx.MessageDialog(
            parent,
            _('Can not select folder %s on server, bailing out.') % folder,
            _('Selecting failed!'),
            wx.OK | wx.ICON_ERROR
        ).ShowModal()
        parent.SetStatusText(_('Export terminated'))
        return

    def msgFilter(sms):
        return (
            (imapConfig.backupRead and sms['SMS'][0]['State'] == 'Read') or
            (imapConfig.backupSent and sms['SMS'][0]['State'] == 'Sent') or
            (imapConfig.backupUnread and sms['SMS'][0]['State'] == 'UnRead')or
            (imapConfig.backupUnsent and sms['SMS'][0]['State'] == 'UnSent')
        )

    messages = filter(msgFilter, messages)
    count = len(messages)

    parent.ShowProgress(_('Saving messages to IMAP'))

    new_messages_num = 0
    count = len(messages)
    for i in range(count):
        if not parent.progress.Update(i * 100 / count):
            del parent.progress
            parent.SetStatusText(_('Export terminated'))
            return

        sms = messages[i]

        filename, data, msgid = Wammu.MailWriter.SMSToMail(parent.cfg, sms, contacts)

        if imapConfig.newMessages:
            res, msgnums = m.search(None, 'HEADER', '"Message-ID" "' + msgid + '"')
            if len(msgnums[0].split()) != 0:
                continue

        new_messages_num += 1

        try:
            res = m.append(folder, '$SMS', None, data)
        except:
            res = ['FAIL']
        if res[0] != 'OK':
            wx.MessageDialog(
                parent,
                _('Can not save message to folder %s on server, bailing out.') % folder,
                _('Saving failed!'),
                wx.OK | wx.ICON_ERROR
            ).ShowModal()
            parent.progress.Update(100)
            del parent.progress
            parent.SetStatusText(_('Export terminated'))
            return

    parent.progress.Update(100)
    del parent.progress

    try:
        m.logout()
    except:
        pass

    if not imapConfig.newMessages:
        parent.SetStatusText(
            _('%(count)d messages exported to "%(path)s" (%(type)s)') % {
                'count': count,
                'path': path,
                'type': _('IMAP server')
            }
        )
    else:
        parent.SetStatusText(
            _('%(new)d new of %(count)d messages exported to "%(path)s" (%(type)s)') % {
                'new': new_messages_num,
                'count': count,
                'path': path,
                'type': _('IMAP server')
            }
        )

def SMSExport(parent, messages, contacts):
    # Select where to export
    dlg = wx.SingleChoiceDialog(
        parent,
        _('Where do you want to export emails created from your messages?'),
        _('Select export type'),
        [_('Mailbox file'), _('Maildir folder'), _('IMAP account')],
        wx.CHOICEDLG_STYLE | wx.RESIZE_BORDER
    )
    if dlg.ShowModal() != wx.ID_OK:
        return

    idx = dlg.GetSelection()
    del dlg

    # Mailbox
    if idx == 0:
        SMSToMailbox(parent, messages, contacts)
    # Maildir
    elif idx == 1:
        SMSToMaildir(parent, messages, contacts)
    # IMAP
    elif idx == 2:
        SMSToIMAP(parent, messages, contacts)
    else:
        raise Exception('Not implemented export functionality!')

def bool2yn(value):
    if value:
        return 'yes'
    else:
        return 'no'

def yn2bool(value):
    return value == 'yes'

class IMAPConfigHelper:
    '''
    A small helper to read and write the Wammu config
    '''
    def __init__(self, WammuConfig):
        self.wcfg = WammuConfig
        self.load()

    def load(self):

        # Textfields
        self.fromAddress = self.wcfg.Read('/MessageExport/From')
        self.server = self.wcfg.Read('/IMAP/Server')
        self.port = self.wcfg.Read('/IMAP/Port')
        self.login = self.wcfg.Read('/IMAP/Login')
        self.password = self.wcfg.Read('/IMAP/Password')

        # Checkboxes
        self.rememberPassword = yn2bool(self.wcfg.Read('/IMAP/RememberPassword'))
        self.useSSL = yn2bool(self.wcfg.Read('/IMAP/UseSSL'))
        self.newMessages = yn2bool(self.wcfg.Read('/IMAP/OnlyNewMessages'))

        # States
        self.backupRead = yn2bool(self.wcfg.Read('/IMAP/BackupStateRead'))
        self.backupSent = yn2bool(self.wcfg.Read('/IMAP/BackupStateSent'))
        self.backupUnread = yn2bool(self.wcfg.Read('/IMAP/BackupStateUnread'))
        self.backupUnsent = yn2bool(self.wcfg.Read('/IMAP/BackupStateUnsent'))

        if self.port == '':
            if self.useSSL:
                self.port = '993'
            else:
                self.port = '143'

    def write(self):

        # Textfields
        self.wcfg.Write('/MessageExport/From', self.fromAddress)
        self.wcfg.Write('/IMAP/Server', self.server)
        self.wcfg.Write('/IMAP/Port', self.port)
        self.wcfg.Write('/IMAP/Login', self.login)
        if self.rememberPassword:
            self.wcfg.Write('/IMAP/Password', self.password)
        else:
            self.wcfg.Write('/IMAP/Password', '')

        # Checkboxes
        self.wcfg.Write('/IMAP/RememberPassword', bool2yn(self.rememberPassword))
        self.wcfg.Write('/IMAP/UseSSL', bool2yn(self.useSSL))
        self.wcfg.Write('/IMAP/OnlyNewMessages', bool2yn(self.newMessages))

        # States
        self.wcfg.Write('/IMAP/BackupStateRead', bool2yn(self.backupRead))
        self.wcfg.Write('/IMAP/BackupStateSent', bool2yn(self.backupSent))
        self.wcfg.Write('/IMAP/BackupStateUnread', bool2yn(self.backupUnread))
        self.wcfg.Write('/IMAP/BackupStateUnsent', bool2yn(self.backupUnsent))


class IMAPSettingsDialog(wx.Dialog):
    def __init__(self, parent, imapConfig):
        wx.Dialog.__init__(self, parent, -1, _("IMAP Settings"), style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)
        self.cfg = imapConfig
        self.connectionFrameSizer_staticbox = wx.StaticBox(self, -1, _("Connection Details"))
        self.preferenciesFrameSizer_staticbox = wx.StaticBox(self, -1, _("Preferences"))
        self.stateFrameSizer_staticbox = wx.StaticBox(self, -1, _("Message State Selection"))
        self.fromAddressLabel = wx.StaticText(self, -1, _("From Address"))
        self.fromAddressTextCtrl = wx.TextCtrl(self, -1, "")
        self.serverLabel = wx.StaticText(self, -1, _("Server"))
        self.serverTextCtrl = wx.TextCtrl(self, -1, "")
        self.portLabel = wx.StaticText(self, -1, _("Port"))
        self.portTextCtrl = wx.TextCtrl(self, -1, "")
        self.loginLabel = wx.StaticText(self, -1, _("Login"))
        self.loginTextCtrl = wx.TextCtrl(self, -1, "")
        self.passwordLabel = wx.StaticText(self, -1, _("Password"))
        self.passwordTextCtrl = wx.TextCtrl(self, -1, "", style=wx.TE_PASSWORD)
        self.rememberCheckBox = wx.CheckBox(self, -1, _("Remember password (insecure)"))
        self.useSSLCheckBox = wx.CheckBox(self, -1, _("Use SSL"))
        self.newMessagesCheckBox = wx.CheckBox(self, -1, _("Only back-up new messages"))
        self.readCheckBox = wx.CheckBox(self, -1, _("Read"))
        self.sentCheckBox = wx.CheckBox(self, -1, _("Sent"))
        self.unreadCheckBox = wx.CheckBox(self, -1, _("Unread"))
        self.unsentCheckBox = wx.CheckBox(self, -1, _("Unsent"))
        self.applyButton = wx.Button(self, wx.ID_APPLY, "")
        self.cancelButton = wx.Button(self, wx.ID_CANCEL, "")
        self.okButton = wx.Button(self, wx.ID_OK, "")

        self.__read_config()
        self.__do_layout()

        self.Bind(wx.EVT_CHECKBOX, self.OnToggleSSL, self.useSSLCheckBox)
        self.Bind(wx.EVT_BUTTON, self.OnOkClick, self.okButton)
        self.Bind(wx.EVT_BUTTON, self.OnApplyClick, self.applyButton)

    def __read_config(self):
        self.fromAddressTextCtrl.SetValue(self.cfg.fromAddress)
        self.serverTextCtrl.SetValue(self.cfg.server)
        self.portTextCtrl.SetValue(self.cfg.port)
        self.loginTextCtrl.SetValue(self.cfg.login)
        self.passwordTextCtrl.SetValue(self.cfg.password)

        self.rememberCheckBox.SetValue(self.cfg.rememberPassword)
        self.useSSLCheckBox.SetValue(self.cfg.useSSL)
        self.newMessagesCheckBox.SetValue(self.cfg.newMessages)

        self.readCheckBox.SetValue(self.cfg.backupRead)
        self.sentCheckBox.SetValue(self.cfg.backupSent)
        self.unreadCheckBox.SetValue(self.cfg.backupUnread)
        self.unsentCheckBox.SetValue(self.cfg.backupUnsent)

    def __copy_config(self):
        self.cfg.fromAddress = self.fromAddressTextCtrl.GetValue()
        self.cfg.server = self.serverTextCtrl.GetValue()
        self.cfg.port = self.portTextCtrl.GetValue()
        self.cfg.login = self.loginTextCtrl.GetValue()
        self.cfg.password = self.passwordTextCtrl.GetValue()

        self.cfg.rememberPassword = self.rememberCheckBox.GetValue()
        self.cfg.useSSL = self.useSSLCheckBox.GetValue()
        self.cfg.newMessages = self.useSSLCheckBox.GetValue()

        self.cfg.backupRead = self.readCheckBox.GetValue()
        self.cfg.backupSent = self.sentCheckBox.GetValue()
        self.cfg.backupUnread = self.unreadCheckBox.GetValue()
        self.cfg.backupUnsent = self.unsentCheckBox.GetValue()

    def __do_layout(self):
        mainSizer = wx.BoxSizer(wx.VERTICAL)
        buttonRowSizer = wx.BoxSizer(wx.HORIZONTAL)
        stateFrameSizer = wx.StaticBoxSizer(self.stateFrameSizer_staticbox, wx.HORIZONTAL)
        preferenciesFrameSizer = wx.StaticBoxSizer(self.preferenciesFrameSizer_staticbox, wx.HORIZONTAL)
        preferenciesGridSizer = wx.FlexGridSizer(3, 2, 2, 2)
        connectionFrameSizer = wx.StaticBoxSizer(self.connectionFrameSizer_staticbox, wx.HORIZONTAL)
        connectionGridSizer = wx.FlexGridSizer(5, 2, 2, 10)
        connectionGridSizer.Add(self.fromAddressLabel, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        connectionGridSizer.Add(self.fromAddressTextCtrl, 0, wx.EXPAND, 0)
        connectionGridSizer.Add(self.serverLabel, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        connectionGridSizer.Add(self.serverTextCtrl, 0, wx.EXPAND, 0)
        connectionGridSizer.Add(self.portLabel, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        connectionGridSizer.Add(self.portTextCtrl, 0, wx.EXPAND, 0)
        connectionGridSizer.Add(self.loginLabel, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        connectionGridSizer.Add(self.loginTextCtrl, 0, wx.EXPAND, 0)
        connectionGridSizer.Add(self.passwordLabel, 0, wx.ALIGN_CENTER_VERTICAL, 0)
        connectionGridSizer.Add(self.passwordTextCtrl, 0, wx.EXPAND, 0)
        connectionGridSizer.AddGrowableCol(1)
        connectionFrameSizer.Add(connectionGridSizer, 1, wx.EXPAND, 0)
        mainSizer.Add(connectionFrameSizer, 0, wx.ALL | wx.EXPAND, 2)
        preferenciesGridSizer.Add((90, 20), 0, 0, 0)
        preferenciesGridSizer.Add(self.rememberCheckBox, 0, 0, 0)
        preferenciesGridSizer.Add((20, 20), 0, 0, 0)
        preferenciesGridSizer.Add(self.useSSLCheckBox, 0, 0, 0)
        preferenciesGridSizer.Add((20, 20), 0, 0, 0)
        preferenciesGridSizer.Add(self.newMessagesCheckBox, 0, 0, 0)
        preferenciesGridSizer.AddGrowableCol(1)
        preferenciesFrameSizer.Add(preferenciesGridSizer, 1, wx.EXPAND, 0)
        mainSizer.Add(preferenciesFrameSizer, 0, wx.ALL | wx.EXPAND, 2)
        stateFrameSizer.Add(self.readCheckBox, 1, wx.EXPAND, 0)
        stateFrameSizer.Add(self.sentCheckBox, 1, wx.EXPAND, 0)
        stateFrameSizer.Add(self.unreadCheckBox, 1, wx.EXPAND, 0)
        stateFrameSizer.Add(self.unsentCheckBox, 1, wx.EXPAND, 0)
        mainSizer.Add(stateFrameSizer, 0, wx.ALL | wx.EXPAND, 2)
        buttonRowSizer.Add((20, 20), 1, wx.EXPAND, 0)
        buttonRowSizer.Add(self.applyButton, 0, wx.ALIGN_BOTTOM, 0)
        buttonRowSizer.Add(self.cancelButton, 0, wx.ALIGN_BOTTOM, 0)
        buttonRowSizer.Add(self.okButton, 0, wx.ALIGN_BOTTOM, 0)
        mainSizer.Add(buttonRowSizer, 1, wx.ALL | wx.EXPAND, 2)
        self.SetSizer(mainSizer)
        mainSizer.Fit(self)
        self.Layout()

    def OnToggleSSL(self, event):
        if self.useSSLCheckBox.GetValue():
            if self.portTextCtrl.GetValue() == '143':
                self.portTextCtrl.SetValue('993')
        else:
            if self.portTextCtrl.GetValue() == '993':
                self.portTextCtrl.SetValue('143')


    def OnApplyClick(self, event):
        self.__copy_config()
        self.cfg.write()

    def OnOkClick(self, event):
        # check for all required fields
        counter = 0
        error = ''
        if self.fromAddressTextCtrl.GetValue() == "":
            counter += 1
            error += _('%d. From Address invalid\n') % counter
        if self.serverTextCtrl.GetValue() == "":
            counter += 1
            error += _('%d. Server incomplete\n') % counter
        if self.portTextCtrl.GetValue() == "" or re.search('\D', self.portTextCtrl.GetValue()):
            counter += 1
            error += _('%d. Port invalid\n') % counter
        if self.loginTextCtrl.GetValue() == "":
            counter += 1
            error += _('%d. Login incomplete\n') % counter
        if self.passwordTextCtrl.GetValue() == "":
            counter += 1
            error += _('%d. Password incomplete\n') % counter
        if  (not self.readCheckBox.GetValue() and
                not self.sentCheckBox.GetValue() and
                not self.unreadCheckBox.GetValue() and
                not self.unsentCheckBox.GetValue()):
            counter += 1
            error += _('%d. No messages to back-up selected. Please tick at least one of the states.') % counter

        if counter != 0:
            wx.MessageDialog(
                self,
                error,
                _('Incomplete'),
                wx.OK | wx.ICON_ERROR
            ).ShowModal()
        else:
            self.__copy_config()
            event.Skip()

# end of class IMAPSettingsDialog
