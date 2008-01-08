# -*- coding: UTF-8 -*-
# vim: expandtab sw=4 ts=4 sts=4:
'''
Wammu - Phone manager
SMS export code.
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
import imaplib
import wx
import Wammu.MailWriter
import Wammu.IMAP

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
            filename, data = Wammu.MailWriter.SMSToMail(parent.cfg, sms, contacts, True)
            f.write(data)
            f.write('\n')
            f.write('\n')

        f.close()
    except IOError:
        del parent.progress
        wx.MessageDialog(parent,
            _('Creating of file %s failed, bailing out.') % path,
            _('Can not create file!'),
            wx.OK | wx.ICON_ERROR).ShowModal()
        del parent.progress
        parent.SetStatusText(_('Export terminated'))
        return

    parent.progress.Update(100)
    del parent.progress
    parent.SetStatusText(_('%(count)d messages exported to "%(path)s" (%(type)s)') % {'count':count, 'path':path, 'type': _('mailbox')})

def SMSToMaildir(parent, messages, contacts):
    count = len(messages)
    dlg = wx.DirDialog(parent, _('Select maildir directory where to save files'), os.getcwd(),
              style=wx.DD_DEFAULT_STYLE|wx.DD_NEW_DIR_BUTTON)

    if dlg.ShowModal() != wx.ID_OK:
        return

    path = dlg.GetPath()
    outpath = path

    if not os.path.isdir(os.path.join(outpath, 'new')):
        res = wx.MessageDialog(parent,
            _('Selected folder does not contain new subfolder and thus probably is not valid maildir.\n\nDo you want to create new subfolder and export to it?'),
            _('Folder doesn\'t look like maildir!'),
            wx.YES_NO | wx.YES_DEFAULT | wx.CANCEL | wx.ICON_WARNING).ShowModal()

        if res == wx.ID_CANCEL:
            return

        if res == wx.ID_YES:
            outpath = os.path.join(outpath, 'new')
            try:
                os.mkdir(outpath)
            except OSError:
                wx.MessageDialog(parent,
                    _('Creating of folder failed, bailing out.'),
                    _('Can not create folder!'),
                    wx.OK | wx.ICON_ERROR).ShowModal()
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
        filename, data = Wammu.MailWriter.SMSToMail(parent.cfg, sms, contacts)

        outfile = os.path.join(outpath, filename)
        if os.path.exists(outfile):
            res = wx.MessageDialog(parent,
                _('Output file already exists, this usually means that this message was already saved there.\n\nDo you wish to overwrite file %s?') % outfile,
                _('File already exists!'),
                wx.YES_NO | wx.NO_DEFAULT | wx.CANCEL | wx.ICON_WARNING).ShowModal()

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
            wx.MessageDialog(parent,
                _('Creating of file %s failed, bailing out.') % outfile,
                _('Can not create file!'),
                wx.OK | wx.ICON_ERROR).ShowModal()
            del parent.progress
            parent.SetStatusText(_('Export terminated'))
            return

    parent.progress.Update(100)
    del parent.progress

    parent.SetStatusText(_('%(count)d messages exported to "%(path)s" (%(type)s)') % {'count':count, 'path':path, 'type': _('maildir')})

def SMSToIMAP(parent, messages, contacts):
    count = len(messages)
    ssl = False
    if wx.MessageDialog(parent,
        _('Do you wish to use SSL while uploading messages to IMAP server?'),
        _('Use SSL?'),
        wx.YES_NO | wx.YES_DEFAULT | wx.ICON_QUESTION).ShowModal() == wx.ID_YES:
        ssl = True

    default_server = parent.cfg.Read('/IMAP/Server')
    dlg = wx.TextEntryDialog(parent,
        _('Please enter server name'),
        _('Server name'),
        default_server)
    if dlg.ShowModal() == wx.ID_CANCEL:
        return
    server = dlg.GetValue()
    parent.cfg.Write('/IMAP/Server', server)

    default_login = parent.cfg.Read('/IMAP/Login')
    dlg = wx.TextEntryDialog(parent,
        _('Please enter login on server %s') % server,
        _('Login'),
        default_login)
    if dlg.ShowModal() == wx.ID_CANCEL:
        return
    login = dlg.GetValue()
    parent.cfg.Write('/IMAP/Login', login)

    if server == default_server and login == default_login:
        default_password = parent.cfg.Read('/IMAP/Password')
    else:
        default_password = ''
    while True:
        dlg = wx.PasswordEntryDialog(parent,
            _('Please enter password for %(login)s@%(server)s') % {'login': login,'server': server},
            _('Password'),
            default_password)
        if dlg.ShowModal() == wx.ID_CANCEL:
            return
        password = dlg.GetValue()

        busy = wx.BusyInfo(_('Connecting to IMAP server...'))

        if ssl:
            m = imaplib.IMAP4_SSL(server)
        else:
            m = imaplib.IMAP4(server)

        try:
            res = m.login(login, password)
        except:
            res = ['FAIL']
        del busy
        if res[0] == 'OK':
            break
        else:
            if wx.MessageDialog(parent,
                _('Can not login, you probably entered invalid login information. Do you want to retry?'),
                _('Login failed!'),
                wx.YES_NO | wx.YES_DEFAULT | wx.ICON_ERROR).ShowModal() == wx.ID_NO:
                return

    if password != default_password:
        if wx.MessageDialog(parent,
            _('Connection suceeded, do you want to remember password? This is a bit insecure.'),
            _('Save password?'),
            wx.YES_NO | wx.NO_DEFAULT | wx.ICON_QUESTION).ShowModal() == wx.ID_YES:
                parent.cfg.Write('/IMAP/Password', password)


    busy = wx.BusyInfo(_('Listing folders on IMAP server...'))
    try:
        res, list = m.list()
    except:
        res = 'FAIL'
    del busy
    if res != 'OK':
        wx.MessageDialog(parent,
            _('Can not list folders on server, bailing out.'),
            _('Listing failed!'),
            wx.OK | wx.ICON_ERROR).ShowModal()
        parent.SetStatusText(_('Export terminated'))
        return

    folders = []
    for item in list:
        vals = item.split('"')
        folders.append(unicode(vals[-2], 'imap4-utf-7'))

    folders.sort()

    dlg = wx.SingleChoiceDialog(parent,
        _('Please select folder on server %s where messages will be stored') % server,
        _('Select folder'),
        folders, wx.CHOICEDLG_STYLE | wx.RESIZE_BORDER)
    if dlg.ShowModal() == wx.ID_CANCEL:
        return
    path = '%s@%s/%s' % (login, server, folders[dlg.GetSelection()])
    folder = folders[dlg.GetSelection()].encode('imap4-utf-7')

    busy = wx.BusyInfo(_('Selecting folder on IMAP server...'))
    try:
        res = m.select(folder)
    except:
        res = ['FAIL']
    del busy
    if res[0] != 'OK':
        wx.MessageDialog(parent,
            _('Can not select folder %s on server, bailing out.') % folder,
            _('Selecting failed!'),
            wx.OK | wx.ICON_ERROR).ShowModal()
        parent.SetStatusText(_('Export terminated'))
        return

    parent.ShowProgress(_('Saving messages to IMAP'))
    for i in range(count):
        if not parent.progress.Update(i * 100 / count):
            del parent.progress
            parent.SetStatusText(_('Export terminated'))
            return

        sms = messages[i]
        filename, data = Wammu.MailWriter.SMSToMail(parent.cfg, sms, contacts)

        try:
            res = m.append(folder, '$SMS', None, data)
        except:
            res = ['FAIL']
        if res[0] != 'OK':
            wx.MessageDialog(parent,
                _('Can not save message to folder %s on server, bailing out.') % folder,
                _('Saving failed!'),
                wx.OK | wx.ICON_ERROR).ShowModal()
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

    parent.SetStatusText(_('%(count)d messages exported to "%(path)s" (%(type)s)') % {'count':count, 'path':path, 'type': _('IMAP server')})

def SMSExport(parent, messages, contacts):
    # Select where to export
    dlg = wx.SingleChoiceDialog(parent, _('Where do you want to export emails created from your messages?'), _('Select export type'),
                                [_('Mailbox file'), _('Maildir folder'), _('IMAP account')], wx.CHOICEDLG_STYLE | wx.RESIZE_BORDER)
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

