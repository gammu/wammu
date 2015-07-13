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
Items browser
'''

import wx
import re
import Wammu
import Wammu.Events
import Wammu.Utils
import Wammu.Paths
from Wammu.Locales import StrConv, ugettext as _

import wx.lib.mixins.listctrl

COLUMN_INFO = {
        'info':
        (
            (
                _('Name'),
                _('Value')
            ),
            (
                'Name',
                'Value'
            ),
        ),
        'contact':
        (
            (
                _('Location'),
                _('Memory'),
                _('Name'),
                _('Number')
            ),
            (
                'Location',
                'MemoryType',
                'Name',
                'Number'
            ),
        ),
        'call':
        (
            (
                _('Location'),
                _('Type'),
                _('Name'),
                _('Number'),
                _('Date')
            ),
            (
                'Location',
                'MemoryType',
                'Name',
                'Number',
                'Date'
            ),
        ),
        'message':
        (
            (
                _('Location'),
                _('Status'),
                _('Number'),
                _('Date'),
                _('Text')
            ),
            (
                'Location',
                'State',
                'Number',
                'DateTime',
                'Text'
            ),
        ),
        'todo':
        (
            (
                _('Location'),
                _('Completed'),
                _('Priority'),
                _('Text'),
                _('Date')
            ),
            (
                'Location',
                'Completed',
                'Priority',
                'Text',
                'Date'
            ),
        ),
        'calendar':
        (
            (
                _('Location'),
                _('Type'),
                _('Start'),
                _('End'),
                _('Text'),
                _('Alarm'),
                _('Recurrence')
            ),
            (
                'Location',
                'Type',
                'Start',
                'End',
                'Text',
                'Alarm',
                'Recurrence'
            ),
        )
}


class FilterException(Exception):
    '''
    Exception which occurs when there is something wrong in filtering
    expression.
    '''
    pass


class Browser(wx.ListCtrl, wx.lib.mixins.listctrl.ListCtrlAutoWidthMixin):
    '''
    Generic class for browsing values.
    '''
    def __init__(self, parent, win, cfg):
        wx.ListCtrl.__init__(
            self,
            parent,
            -1,
            style=wx.LC_REPORT | wx.LC_VIRTUAL | wx.LC_HRULES | wx.LC_VRULES
        )
        self.win = win
        self.cfg = cfg

        self.itemno = -1
        self.type = ''
        self.values = []
        self.allvalues = []
        self.sortkey = ''
        self.sortorder = 1
        self.columns = []
        self.keys = []
        self.popup_index = -1

        color = wx.SystemSettings.GetColour(wx.SYS_COLOUR_3DLIGHT)

        self.attr1 = wx.ListItemAttr()

        self.attr2 = wx.ListItemAttr()
        self.attr2.SetBackgroundColour(color)

        self.attr3 = wx.ListItemAttr()
        fnt = self.attr3.GetFont()
        fnt.SetStyle(wx.FONTSTYLE_ITALIC)
        self.attr3.SetFont(fnt)

        self.attr4 = wx.ListItemAttr()
        self.attr4.SetBackgroundColour(color)
        self.attr4.SetFont(fnt)

        image_list = wx.ImageList(16, 16)
        down_bitmap = wx.Bitmap(Wammu.Paths.MiscPath('downarrow'))
        up_bitmap = wx.Bitmap(Wammu.Paths.MiscPath('uparrow'))
        self.downarrow = image_list.Add(down_bitmap)
        self.uparrow = image_list.Add(up_bitmap)
        self.AssignImageList(image_list, wx.IMAGE_LIST_SMALL)

        wx.lib.mixins.listctrl.ListCtrlAutoWidthMixin.__init__(self)

        # Create IDs for popup menu
        self.popup_id_send = wx.NewId()
        self.popup_id_edit = wx.NewId()
        self.popup_id_message = wx.NewId()
        self.popup_id_contact = wx.NewId()
        self.popup_id_call = wx.NewId()
        self.popup_id_delete = wx.NewId()
        self.popup_id_delete_selection = wx.NewId()
        self.popup_id_duplicate = wx.NewId()
        self.popup_id_reply = wx.NewId()
        self.popup_id_backup_one = wx.NewId()
        self.popup_id_backup_selection = wx.NewId()
        self.popup_id_backup_all = wx.NewId()

        self.BindEvents()

    def BindEvents(self):
        '''
        Bind various event handlers to events we need.
        '''
        self.Bind(
            wx.EVT_LIST_ITEM_SELECTED,
            self.OnItemSelected,
            self
        )
        self.Bind(
            wx.EVT_LIST_ITEM_ACTIVATED,
            self.OnItemActivated,
            self
        )
        self.Bind(
            wx.EVT_LIST_KEY_DOWN,
            self.OnKey,
            self
        )
        self.Bind(
            wx.EVT_LIST_COL_CLICK,
            self.OnColClick,
            self
        )
        self.Bind(
            wx.EVT_LIST_ITEM_RIGHT_CLICK,
            self.OnRightClick,
            self
        )
        self.Bind(
            wx.EVT_MENU,
            self.OnPopupSend,
            id=self.popup_id_send
        )
        self.Bind(
            wx.EVT_MENU,
            self.OnPopupEdit,
            id=self.popup_id_edit
        )
        self.Bind(
            wx.EVT_MENU,
            self.OnPopupMessage,
            id=self.popup_id_message
        )
        self.Bind(
            wx.EVT_MENU,
            self.OnPopupContact,
            id=self.popup_id_contact
        )
        self.Bind(
            wx.EVT_MENU,
            self.OnPopupCall,
            id=self.popup_id_call
        )
        self.Bind(
            wx.EVT_MENU,
            self.OnPopupDelete,
            id=self.popup_id_delete
        )
        self.Bind(
            wx.EVT_MENU,
            self.OnPopupDeleteSel,
            id=self.popup_id_delete_selection
        )
        self.Bind(
            wx.EVT_MENU,
            self.OnPopupDuplicate,
            id=self.popup_id_duplicate
        )
        self.Bind(
            wx.EVT_MENU,
            self.OnPopupReply,
            id=self.popup_id_reply
        )
        self.Bind(
            wx.EVT_MENU,
            self.OnPopupBackupOne,
            id=self.popup_id_backup_one
        )
        self.Bind(
            wx.EVT_MENU,
            self.OnPopupBackupSel,
            id=self.popup_id_backup_selection
        )
        self.Bind(
            wx.EVT_MENU,
            self.OnPopupBackupAll,
            id=self.popup_id_backup_all
        )

    def ShowHeaders(self):
        '''
        Updates which headers and keys should be show and displays them.
        '''
        self.columns = COLUMN_INFO[self.type][0]
        self.keys = COLUMN_INFO[self.type][1]

        cnt = len(self.columns)

        for i in range(cnt):
            self.InsertColumn(i, self.columns[i])

        # resize columns to fit content

        # FIXME: this should be acquired better!
        spc = 10

        maxval = [0] * cnt
        for i in range(cnt):
            size = self.GetTextExtent(StrConv(self.columns[i]))[0]
            # 16 bellow is for sort arrrow
            if size + 16 > maxval[i]:
                maxval[i] = size + 16

        for current in self.values:
            for i in range(cnt):
                size = self.GetTextExtent(StrConv(current[self.keys[i]]))
                if size[0] > maxval[i]:
                    maxval[i] = size[0]
        for i in range(cnt - 1):
            self.SetColumnWidth(i, maxval[i] + spc)
        self.resizeLastColumn(maxval[cnt - 1] + spc)

    def Filter(self, text, filter_type):
        '''
        Filters content of browser by various expressions (type of expression
        is defined by filter_type).
        '''
        if text == '':
            self.values = self.allvalues
        else:
            num = None
            if text.isdigit():
                num = int(text)
            if filter_type == 0:
                match = re.compile('.*%s.*' % re.escape(text), re.I)
            elif filter_type == 1:
                try:
                    match = re.compile(text, re.I)
                except:
                    raise FilterException('Failed to compile regexp')
            elif filter_type == 2:
                text = text.replace('*', '__SEARCH_ALL__')
                text = text.replace('?', '__SEARCH_ONE__')
                text = re.escape(text)
                text = text.replace('\\_\\_SEARCH\\_ALL\\_\\_', '.*')
                text = text.replace('\\_\\_SEARCH\\_ONE\\_\\_', '.')
                match = re.compile('.*%s.*' % text, re.I)
            else:
                raise Exception('Unsupported filter type %s!' % filter_type)
            self.values = [
                item for item in self.allvalues
                if Wammu.Utils.MatchesText(item, match, num)
            ]
        self.SetItemCount(len(self.values))
        self.RefreshView()
        self.ShowRow(0)

    def Sorter(self, item1, item2):
        '''
        Compare function for internal list of values.
        '''
        if self.sortkey == 'Location' and isinstance(item1[self.sortkey], str):
            return self.sortorder * cmp(
                int(item1[self.sortkey].split(',')[0]),
                int(item2[self.sortkey].split(', ')[0]))
        elif item1[self.sortkey] is None:
            return -self.sortorder
        elif item2[self.sortkey] is None:
            return self.sortorder
        return self.sortorder * cmp(item1[self.sortkey], item2[self.sortkey])

    def ShowLocation(self, loc, second=None):
        '''
        Shows row which is stored on defined location. Search can be extended
        by specifiyng second tupe of search attribute and value.
        '''
        result = Wammu.Utils.SearchLocation(self.values, loc, second)
        if result != -1:
            self.ShowRow(result)

    def ShowRow(self, index):
        '''
        Activates id-th row.
        '''
        if (self.GetItemCount() > index and index >= 0 and
                self.GetCountPerPage() > 0):
            self.itemno = index

            while self.GetFirstSelected() != -1:
                self.SetItemState(
                    self.GetFirstSelected(), 0, wx.LIST_STATE_SELECTED
                )

            self.SetItemState(
                index,
                wx.LIST_STATE_FOCUSED | wx.LIST_STATE_SELECTED,
                wx.LIST_STATE_FOCUSED | wx.LIST_STATE_SELECTED
            )
            self.EnsureVisible(index)
        else:
            evt = Wammu.Events.ShowEvent(data=None)
            wx.PostEvent(self.win, evt)

    def Change(self, newtype, values):
        '''
        Change type of browser component.
        '''
        if self.type != '':
            self.cfg.Write(
                '/BrowserSortKey/%s' % self.type, self.sortkey
            )
            self.cfg.WriteInt(
                '/BrowserSortOrder/%s' % self.type, self.sortorder
            )
        self.type = newtype
        self.values = values
        self.allvalues = values
        self.sortkey = ''
        self.sortorder = 1
        self.ClearAll()
        self.SetItemCount(len(values))
        self.ShowHeaders()
        # restore sort order
        found = False
        readsort = self.cfg.Read('/BrowserSortKey/%s' % self.type)
        readorder = self.cfg.ReadInt('/BrowserSortOrder/%s' % self.type)
        for i in range(len(self.keys)):
            if self.keys[i] == readsort:
                if readorder == -1:
                    self.sortkey = readsort
                self.Resort(i)
                found = True
        if not found:
            self.Resort(0)

    def Resort(self, col):
        '''
        Changes sort order of listing.
        '''
        # remember show item
        try:
            item = self.values[self.itemno]
        except IndexError:
            item = None
        # find keys and order
        nextsort = self.keys[col]
        if nextsort == self.sortkey:
            self.sortorder = -1 * self.sortorder
        else:
            self.sortorder = 1
        self.sortkey = nextsort

        # do the real sort
        self.values.sort(self.Sorter)

        # set image
        for i in range(self.GetColumnCount()):
            self.ClearColumnImage(i)
        if self.sortorder == 1:
            image = self.downarrow
        else:
            image = self.uparrow
        self.SetColumnImage(col, image)
        self.RefreshView()

        if item is not None:
            self.ShowRow(self.values.index(item))

    def RefreshView(self):
        '''
        Refresh displayed items.
        '''
        if self.GetItemCount() != 0:
            top = self.GetTopItem()
            if top < 0:
                top = 0
            count = self.GetCountPerPage()
            totalcount = self.GetItemCount()
            if count < 0:
                count = totalcount
            last = min(totalcount - 1, top + count)
            self.RefreshItems(top, last)

    def OnKey(self, evt):
        '''
        Key handler which catches delete key for deletion of current item and
        R/r key for message reply.
        '''
        if evt.GetKeyCode() == wx.WXK_DELETE:
            self.DoSelectedDelete()
        elif evt.GetKeyCode() in [114, 82]:
            self.DoReply()

    def DoSelectedDelete(self):
        '''
        Delete selected message.
        '''
        lst = []
        index = self.GetFirstSelected()
        while index != -1:
            lst.append(self.values[index])
            index = self.GetNextSelected(index)
        self.DoDelete(lst)

    def DoDelete(self, lst):
        '''
        Send delete event to parent.
        '''
        evt = Wammu.Events.DeleteEvent(lst=lst)
        wx.PostEvent(self.win, evt)

    def DoBackup(self, lst):
        '''
        Send backup event to parent.
        '''
        evt = Wammu.Events.BackupEvent(lst=lst)
        wx.PostEvent(self.win, evt)

    def DoReply(self):
        '''
        Send reply event to parent.
        '''
        evt = Wammu.Events.ReplyEvent(data=self.values[self.GetFocusedItem()])
        wx.PostEvent(self.win, evt)

    def OnRightClick(self, evt):
        '''
        Handle right click - show context menu with correct options for
        current type of listing.
        '''
        if self.type == 'info':
            return
        self.popup_index = evt.m_itemIndex

        # make a menu
        menu = wx.Menu()

        # add some items
        if self.popup_index != -1 and self.type == 'message':
            if self.values[evt.m_itemIndex]['State'] == 'Sent':
                menu.Append(self.popup_id_send, _('Resend'))
            if self.values[evt.m_itemIndex]['State'] == 'UnSent':
                menu.Append(self.popup_id_send, _('Send'))
            if self.values[evt.m_itemIndex]['State'] in ('Read', 'UnRead'):
                menu.Append(self.popup_id_reply, _('Reply'))
            if self.values[evt.m_itemIndex]['Number'] != '':
                menu.Append(self.popup_id_call, _('Call'))
            menu.AppendSeparator()

        if self.popup_index != -1 and self.type in ['contact', 'call']:
            menu.Append(self.popup_id_message, _('Send message'))
            menu.Append(self.popup_id_call, _('Call'))
            if self.popup_index != -1 and self.type in ['call']:
                menu.Append(self.popup_id_contact, _('Store as new contact'))
            menu.AppendSeparator()

        if self.popup_index != -1 and self.type not in ['call', 'message']:
            menu.Append(self.popup_id_edit, _('Edit'))
        if self.popup_index != -1 and self.type not in ['call']:
            menu.Append(self.popup_id_duplicate, _('Duplicate'))
            menu.AppendSeparator()

        if self.popup_index != -1:
            menu.Append(self.popup_id_delete, _('Delete current'))
        menu.Append(self.popup_id_delete_selection, _('Delete selected'))

        menu.AppendSeparator()
        if self.popup_index != -1:
            menu.Append(self.popup_id_backup_one, _('Backup current'))
        menu.Append(self.popup_id_backup_selection, _('Backup selected'))
        menu.Append(self.popup_id_backup_all, _('Backup all'))

        # Popup the menu.  If an item is selected then its handler
        # will be called before PopupMenu returns.
        self.PopupMenu(menu, evt.GetPoint())

    def OnPopupDuplicate(self, event):
        evt = Wammu.Events.DuplicateEvent(data=self.values[self.popup_index])
        wx.PostEvent(self.win, evt)

    def OnPopupReply(self, event):
        evt = Wammu.Events.ReplyEvent(data=self.values[self.popup_index])
        wx.PostEvent(self.win, evt)

    def OnPopupSend(self, event):
        evt = Wammu.Events.SendEvent(data=self.values[self.popup_index])
        wx.PostEvent(self.win, evt)

    def OnPopupCall(self, event):
        evt = Wammu.Events.CallEvent(data=self.values[self.popup_index])
        wx.PostEvent(self.win, evt)

    def OnPopupMessage(self, event):
        evt = Wammu.Events.MessageEvent(data=self.values[self.popup_index])
        wx.PostEvent(self.win, evt)

    def OnPopupContact(self, event):
        data = self.values[self.popup_index]
        data['Location'] = 0
        data['MemoryType'] = 'ME'
        evt = Wammu.Events.EditEvent(data=data)
        wx.PostEvent(self.win, evt)

    def OnPopupEdit(self, event):
        evt = Wammu.Events.EditEvent(data=self.values[self.popup_index])
        wx.PostEvent(self.win, evt)

    def OnPopupDelete(self, event):
        self.DoDelete([self.values[self.popup_index]])

    def OnPopupDeleteSel(self, event):
        self.DoSelectedDelete()

    def OnPopupBackupOne(self, event):
        self.DoBackup([self.values[self.popup_index]])

    def OnPopupBackupSel(self, event):
        item_list = []
        index = self.GetFirstSelected()
        while index != -1:
            item_list.append(self.values[index])
            index = self.GetNextSelected(index)
        self.DoBackup(item_list)

    def OnPopupBackupAll(self, event):
        self.DoBackup(self.values)

    def OnColClick(self, evt):
        self.Resort(evt.GetColumn())

    def OnItemSelected(self, event):
        self.itemno = event.m_itemIndex
        evt = Wammu.Events.ShowEvent(data=self.values[event.m_itemIndex])
        wx.PostEvent(self.win, evt)

    def OnItemActivated(self, event):
        evt = Wammu.Events.EditEvent(data=self.values[event.m_itemIndex])
        wx.PostEvent(self.win, evt)

    def getColumnText(self, index, col):
        item = self.GetItem(index, col)
        return item.GetText()

    def OnGetItemText(self, item, col):
        '''
        Get item text.
        '''
        if item >= len(self.values):
            return None
        return StrConv(self.values[item][self.keys[col]])

    def OnGetItemAttr(self, item):
        '''
        Get item attributes - highlight synced items, make odd and even rows
        different.
        '''
        if self.values[item]['Synced']:
            if item % 2 == 1:
                return self.attr1
            else:
                return self.attr2
        if item % 2 == 1:
            return self.attr3
        else:
            return self.attr4
