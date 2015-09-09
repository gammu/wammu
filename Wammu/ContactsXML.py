# -*- coding: UTF-8 -*-
#
# Copyright © 2008 Florent Kaisser <florent.kaisser@free.fr>
# Copyright © 2012 Andriy Grytsenko <andrej@rep.kiev.ua>
# Copyright © 2015 Michal Čihař <michal@cihar.com>
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
Module for writing contacts to XML.
'''

from Wammu.Locales import ugettext as _
import Wammu.Data
from xml.sax.saxutils import escape
import wx
import os

XMLheader = '<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n<?xml-stylesheet type=\"text/xsl\" href=\"sms.xsl\"?>\n'




def ContactToXML(cfg, folder, contact):
    '''
    Convert a contact to XML
    '''

    addr_zip = ''
    addr_street = ''
    addr_city = ''
    addr_state = ''
    addr_country = ''

    contactxml = "    <contact>\n"

    contactxml += "        <name>"
    contactxml += escape(contact['Name'].encode('utf-8'))
    contactxml += "</name>\n"

    for i in contact['Entries']:
        if i['Type'] == 'Text_Zip':
            addr_zip = i['Value']
        elif i['Type'] == 'Text_StreetAddress':
            addr_street = i['Value']
        elif i['Type'] == 'Text_City':
            addr_city = i['Value']
        elif i['Type'] == 'Text_State':
            addr_state = i['Value']
        elif i['Type'] == 'Text_Country':
            addr_country = i['Value']
        elif i['Type'] == 'Text_Note':
            contactxml += "        <note>"
            contactxml += escape(i['Value'].encode('utf-8'))
            contactxml += "</note>\n"
        elif i['Type'] == 'Text_URL':
            contactxml += "        <url>"
            contactxml += escape(i['Value'].encode('utf-8'))
            contactxml += "</url>\n"
        elif i['Type'] == 'Text_Email':
            if i['Value']:
                contactxml += "        <email>"
                contactxml += escape(i['Value'].encode('utf-8'))
                contactxml += "</email>\n"
        elif i['Type'] == 'Text_Email2':
            if i['Value']:
                contactxml += "        <email>"
                contactxml += escape(i['Value'].encode('utf-8'))
                contactxml += "</email>\n"
        elif i['Type'] == 'Number_Mobile':
            contactxml += "        <mobile>"
            contactxml += escape(i['Value'].encode('utf-8'))
            contactxml += "</mobile>\n"
        elif i['Type'] == 'Number_Work':
            contactxml += "        <work>"
            contactxml += escape(i['Value'].encode('utf-8'))
            contactxml += "</work>\n"
        elif i['Type'] == 'Number_Fax':
            contactxml += "        <fax>"
            contactxml += escape(i['Value'].encode('utf-8'))
            contactxml += "</fax>\n"
        elif i['Type'] == 'Number_Home':
            contactxml += "        <home>"
            contactxml += escape(i['Value'].encode('utf-8'))
            contactxml += "</home>\n"
        elif i['Type'][:7] == 'Number_':
            contactxml += "        <phone>"
            contactxml += escape(i['Value'].encode('utf-8'))
            contactxml += "</phone>\n"

    addr_full = addr_zip
    if addr_street:
        if addr_full:
            addr_full += ','
        addr_full += addr_street
    if addr_city:
        if addr_full:
            addr_full += ','
        addr_full += addr_city
    if addr_state:
        if addr_full:
            addr_full += ','
        addr_full += addr_state
    if addr_country:
        if addr_full:
            addr_full += ','
        addr_full += addr_country
    if addr_full:
        contactxml += "        <address>"
        contactxml += escape(addr_full.encode('utf-8'))
        contactxml += "</address>\n"

    if contact['Date'] is not None:

        contactxml += "        <birthday>"
        contactxml += contact['Date'].strftime("%d.%m.%Y")
        contactxml += "</birthday>\n"

    contactxml += "        <folder>"
    contactxml += escape(folder.encode('utf-8'))
    contactxml += "</folder>\n"

    contactxml += "    </contact>\n"

    return contactxml

def ContactsExportXML(parent, contactsSM, contactsME):
    countSM = len(contactsSM)
    countME = len(contactsME)
    count = countSM + countME
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
    if os.path.splitext(path)[1] == '' and ext is not None:
        path += '.' + ext

    parent.ShowProgress(_('Saving contacts to XML'))
    try:
        f = file(path, 'w')
        f.write(XMLheader)
        f.write("<contacts>\n")
        for i in range(countSM):
            if not parent.progress.Update(i * 100 / count):
                del parent.progress
                parent.SetStatusText(_('Export terminated'))
                return

            contact = contactsSM[i]
            data = Wammu.ContactsXML.ContactToXML(parent.cfg, 'SIM', contact)

            f.write(data)

        for i in range(countME):
            if not parent.progress.Update((countSM + i) * 100 / count):
                del parent.progress
                parent.SetStatusText(_('Export terminated'))
                return

            contact = contactsME[i]
            data = Wammu.ContactsXML.ContactToXML(parent.cfg, _('phone'), contact)

            f.write(data)

        f.write("</contacts>\n")
        f.close()
    except IOError:
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
    parent.SetStatusText(_('%(count)d contacts exported to "%(path)s"') % {
        'count': count,
        'path': path
    })
