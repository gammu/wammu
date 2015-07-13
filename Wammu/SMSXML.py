# -*- coding: UTF-8 -*-
#
# Copyright © 2008 Florent Kaisser <florent.kaisser@free.fr>
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
Module for writing SMS to XML.
'''

from Wammu.Utils import SearchNumber
from Wammu.MessageDisplay import SmsTextFormat
from Wammu.Locales import ugettext as _
import Wammu.Data
import wx
import os

XMLheader = '<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n<?xml-stylesheet type=\"text/xsl\" href=\"sms.xsl\"?>\n'




def SMSToXML(cfg, sms, contact=None):
    '''
    Convert a sms to XML
    '''


    text = SmsTextFormat(cfg, sms['Text'], doxml=True)

    smsxml = "    <message>\n"

    if sms['DateTime'] is not None:

        smsxml += "        <date>"
        smsxml += sms['DateTime'].strftime("%d.%m.%Y %H:%M:%S")
        smsxml += "</date>\n"

        smsxml += "        <dateenc>"
        smsxml += sms['DateTime'].strftime("%Y%m%d%H%M%S")
        smsxml += "</dateenc>\n"

    smsxml += "        <text>"
    smsxml += text.encode('utf-8')
    smsxml += "</text>\n"

    smsxml += "        <telephone>"
    smsxml += sms['Number'].encode('utf-8')
    smsxml += "</telephone>\n"

    smsxml += "        <contact>"
    smsxml += contact.encode('utf-8')
    smsxml += "</contact>\n"

    smsxml += "        <folder>"
    smsxml += str(sms['Folder'])
    smsxml += "</folder>\n"

    smsxml += "        <stat>"
    smsxml += sms['State']
    smsxml += "</stat>\n"

    smsxml += "    </message>\n"

    return smsxml

def SMSExportXML(parent, messages, contacts):
    count = len(messages)
    wildcard = _('XML File') + ' (*.xml)|*.xml|' + _('All files') + ' (*.*)|*.*;*'
    exts = ['xml']
    exts.append(None)
    dlg = wx.FileDialog(parent, _('Select XML file...'), os.getcwd(), "", wildcard, wx.SAVE | wx.OVERWRITE_PROMPT | wx.CHANGE_DIR)

    if dlg.ShowModal() != wx.ID_OK:
        return

    path = dlg.GetPath()
    ext = exts[dlg.GetFilterIndex()]
    # Add automatic extension if we know one and file does not
    # have any
    if (os.path.splitext(path)[1] == '' and
            ext is not None):
        path += '.' + ext

    parent.ShowProgress(_('Saving messages to XML'))
    try:
        f = file(path, 'w')
        f.write(XMLheader)
        f.write("<messages>\n")
        for i in range(count):
            if not parent.progress.Update(i * 100 / count):
                del parent.progress
                parent.SetStatusText(_('Export terminated'))
                return

            sms = messages[i]
            j = SearchNumber(contacts, sms['Number'])
            if j == -1:
                contact = sms['Number']
            else:
                contact = contacts[j]['Name']
            data = Wammu.SMSXML.SMSToXML(parent.cfg, sms, contact)

            f.write(data)

        f.write("</messages>\n")
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
