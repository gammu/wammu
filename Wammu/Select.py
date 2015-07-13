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
Contact and phone number select dialogs
'''

import wx
import Wammu.Utils
from Wammu.Locales import StrConv
from Wammu.Locales import ugettext as _

def SortName(item1, item2):
    '''
    Comparator function for sorting by name.
    '''
    return cmp(item1['Name'], item2['Name'])

def SelectContact(parent, contactlist, index=False):
    '''
    Dialog for selecting contact.
    '''
    contactlist.sort(SortName)
    choices = []
    for entry in contactlist:
        if entry['Name'] == '':
            choices.append(StrConv(entry['Number']))
        else:
            choices.append(StrConv(entry['Name']))

    dlg = wx.SingleChoiceDialog(
            parent,
            _('Select contact from below list'),
            _('Select contact'),
            choices,
            wx.CHOICEDLG_STYLE | wx.RESIZE_BORDER)
    if dlg.ShowModal() == wx.ID_OK and len(choices) > 0:
        result = dlg.GetSelection()
        if not index:
            result = contactlist[result]['Location']
    else:
        result = -1
    del dlg
    return result

def SelectNumber(parent, contactlist):
    '''
    Allows user to select number from phone list. First it asks for contact
    and then which number to use.
    '''
    i = SelectContact(parent, contactlist, True)
    if i == -1:
        return None
    return SelectContactNumber(parent, contactlist[i])

def SelectContactNumber(parent, item):
    '''
    Selects number of chosen contact. If it has single number, it returns it
    directly, otherwise user has to select which number to use.
    '''
    numbers = []
    texts = []
    for i in range(len(item['Entries'])):
        if Wammu.Utils.GetItemType(item['Entries'][i]['Type']) == 'phone':
            numbers.append(item['Entries'][i]['Value'])
            texts.append(StrConv(u'%s : %s' % (
                item['Entries'][i]['Type'],
                item['Entries'][i]['Value'])))

    if len(numbers) == 0:
        return None
    elif len(numbers) == 1:
        return numbers[0]
    dlg = wx.SingleChoiceDialog(
            parent,
            _('Select number for selected contact'),
            _('Select phone number'),
            texts,
            wx.CHOICEDLG_STYLE | wx.RESIZE_BORDER)
    if dlg.ShowModal() == wx.ID_OK:
        result = numbers[dlg.GetSelection()]
    else:
        result = None
    del dlg
    return result
